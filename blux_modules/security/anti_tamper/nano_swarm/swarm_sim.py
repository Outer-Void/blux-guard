#!/usr/bin/env python3
"""
swarm_sim.py — Defensive nano-swarm with YARA, network monitoring, and TUI
"""

import os
import sys
import time
import json
import hmac
import hashlib
import base64
import secrets
import subprocess
from cryptography.fernet import Fernet
import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Thread
from queue import Queue, Empty
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
from datetime import datetime, timedelta

# Third-party library imports
try:
    import yara
    YARA_AVAILABLE = True
except ImportError:
    YARA_AVAILABLE = False
    print("YARA not available. Please install with 'pip install yara-python'")
try:
    from textual.app import App, ComposeResult
    from textual.widgets import Header, Footer, Static, DataTable, Markdown
    from textual.containers import Vertical, Horizontal
    from textual.reactive import reactive
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    print("Textual not available. Please install with 'pip install textual'")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ---- Configuration (Environment Variables) ----
HOME = Path.home()
INC_DIR = Path(os.environ.get("SWARM_INCIDENT_DIR", str(HOME / ".tripengine")))
YARA_RULES_DIR = Path(os.environ.get("SWARM_YARA_RULES_DIR", str(HOME / ".tripengine" / "yara_rules")))
OUTBOX = INC_DIR / "outbox" # Not needed
SECRET_FILE = INC_DIR / "secret.key"
# Fernet encryption key file (used for encrypting secrets)
FERNET_KEY_FILE = INC_DIR / "fernet.key"
QUARANTINE_SCRIPT = Path(os.environ.get("SWARM_QUARANTINE_SCRIPT", str(HOME / "bin" / "quarantine_apk.sh")))
NUM_AGENTS = int(os.environ.get("SWARM_NUM_AGENTS", "5"))
WATCH_DIRECTORIES = os.environ.get("SWARM_WATCH_DIRS", f"{HOME / 'Download'},/sdcard/Download").split(",")
ALERT_COOLDOWN = int(os.environ.get("SWARM_ALERT_COOLDOWN", "60"))  # seconds

# ---- Ensure Directories Exist ----
INC_DIR.mkdir(exist_ok=True, parents=True)
YARA_RULES_DIR.mkdir(exist_ok=True, parents=True)

# Load YARA rules
if YARA_AVAILABLE:
    try:
        rules = yara.compile(YARA_RULES_DIR / "index.yar")  # Assuming rules are in index.yar
        logger.info(f"Loaded YARA rules from {YARA_RULES_DIR / 'index.yar'}")
    except yara.Error as e:
        rules = None
        logger.error(f"Error compiling YARA rules: {e}")
else:
    rules = None  # YARA not available

# --- Secret Key Rotation Logic ---
def get_fernet_key():
    """
    Loads the Fernet encryption key from disk, or generates and saves one if missing.
    Fernet key itself is stored with restrictive permissions.
    """
    if not FERNET_KEY_FILE.exists():
        key = Fernet.generate_key()
        FERNET_KEY_FILE.write_bytes(key)
        os.chmod(str(FERNET_KEY_FILE), 0o600)
        logger.info(f"Generated new Fernet key at {FERNET_KEY_FILE}")
        return key
    return FERNET_KEY_FILE.read_bytes()

def get_secret_key():
    """
    Generates a secret key or retrieves it from a file, rotating it daily.
    Key is encrypted at rest using Fernet symmetric encryption.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    key_file_name = f"secret_{today}.key"
    key_file_path = INC_DIR / key_file_name
    fernet_key = get_fernet_key()
    fernet = Fernet(fernet_key)
    try:
        if key_file_path.exists():
            # Read and decrypt secret
            encrypted_secret = key_file_path.read_bytes()
            return fernet.decrypt(encrypted_secret)
        else:
            # Generate new key
            new_secret = secrets.token_hex(32).encode()
            # Delete old secret keys except for the current one
            for file in INC_DIR.glob("secret_*.key"):
                if file != key_file_path:
                    try:
                        file.unlink()
                    except Exception as e:
                        logger.error(f"Error deleting old secret file {file}: {e}")
            # Encrypt and write the new secret and protect it
            encrypted_secret = fernet.encrypt(new_secret)
            key_file_path.write_bytes(encrypted_secret)
            os.chmod(str(key_file_path), 0o600)
            logger.info(f"Generated and saved new encrypted secret key at {key_file_path}")
            return new_secret
    except Exception as e:
        logger.error(f"Error handling secret key: {e}")
        return None  # Handle this in calling functions

SECRET = get_secret_key()

if not SECRET:
    logger.critical("Failed to load or generate secret key. Exiting.")
    sys.exit(1)

# ---- Global Rate Limiter ----
last_alert_time = {}  # Dictionary to track last alert time for each agent

# ---- helpers ----
def sign_and_append(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Signs a payload using HMAC-SHA256.

    Args:
        payload: The dictionary to sign.

    Returns:
        The entry (dictionary) that was written, or None.
    """
    if not SECRET:
        logger.error("Cannot sign event: No secret key available.")
        return None

    canon = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    try:
        sig = base64.b64encode(hmac.new(SECRET, canon, hashlib.sha256).digest()).decode()
        entry = {"ts": int(time.time()), "payload_b64": base64.b64encode(canon).decode(), "sig": sig}
        with open(INC_DIR / "incidents.jsonl", "a") as f:
            f.write(json.dumps(entry, separators=(",", ":")) + "\n")
        return entry
    except Exception as e:
        logger.exception(f"Error signing and appending payload: {e}")
        return None

def do_quarantine(apk_path: str) -> Tuple[bool, str]:
    """Executes the quarantine script on the given APK path.

    Args:
        apk_path: The path to the APK file.

    Returns:
        A tuple containing a boolean indicating success and a message string.
    """
    if not QUARANTINE_SCRIPT.exists():
        logger.warning(f"Quarantine script not found: {QUARANTINE_SCRIPT}")
        return False, "no_quarantine_script"

    if not os.path.exists(apk_path):
        logger.warning(f"File not found for quarantine: {apk_path}")
        return False, "file_not_found"

    try:
        proc = subprocess.run([str(QUARANTINE_SCRIPT), apk_path],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
        ok = proc.returncode == 0
        msg = proc.stdout.strip() if ok else proc.stderr.strip()
        if not ok:
            logger.error(f"Quarantine script failed for {apk_path}: {msg}")
        else:
            logger.info(f"Quarantine script succeeded for {apk_path}")
        return ok, msg
    except subprocess.TimeoutExpired:
        logger.error(f"Quarantine script timed out for {apk_path}")
        return False, "timeout"
    except Exception as e:
        logger.exception(f"Error running quarantine script: {e}")
        return False, str(e)

# ---- agent ----
class Agent(Thread):
    """A thread that processes events from a queue"""

    def __init__(self, id: int, event_q: Queue, app: 'SwarmApp'):
        super().__init__(daemon=True)
        self.id = id
        self.q = event_q
        self.app = app # Reference to the Textual app for UI updates
        self.executor = ThreadPoolExecutor(max_workers=2)  # For non-blocking quarantine
        self.loop = asyncio.get_event_loop()

    def run(self):
        logger.info(f"[agent-{self.id}] started")
        while True:
            try:
                evt = self.q.get(timeout=1)
            except Empty:
                continue
            self.loop.run_until_complete(self.handle_event(evt))

    async def handle_event(self, evt: Dict[str, Any]):
        try:
            event_type = evt.get("type")
            if event_type == "apk_new":
                await self.handle_apk_new(evt)
            elif event_type == "network_fastflux":
                await self.handle_network_fastflux(evt)
            else:
                await self.handle_generic_event(evt)
        except Exception as e:
            logger.exception(f"[agent-{self.id}] Error handling event: {e}")

    async def handle_apk_new(self, evt: Dict[str, Any]):
        """Handles a new APK event."""
        pid = secrets.token_hex(8)
        path = evt.get("path")
        alert = {"id": pid, "agent": self.id, "type": "apk_new", "path": path, "ts": int(time.time())}

        # YARA scan
        yara_matches = None
        if YARA_AVAILABLE and rules and os.path.exists(path):
            try:
                yara_matches = rules.match(path)
                if yara_matches:
                    alert["yara_matches"] = [str(match) for match in yara_matches]
                    self.app.add_alert(alert) # update GUI

            except Exception as e:
                logger.error(f"[agent-{self.id}] YARA scan error: {e}")

        # Quarantine
        future = self.loop.run_in_executor(self.executor, do_quarantine, path)
        ok, msg = await future
        alert["quarantine"] = {"ok": ok, "msg": msg, "target": path}
        logger.info(f"[agent-{self.id}] Handled new APK: {path} (YARA: {yara_matches}, Quarantine: {ok})")

        if sign_and_append(alert):
            logger.info(f"[agent-{self.id}] Appended incident to incidents.jsonl")
        else:
            logger.error(f"[agent-{self.id}] Could not sign alert")

    async def handle_network_fastflux(self, evt: Dict[str, Any]):
        pid = secrets.token_hex(8)
        uid = evt.get("uid")
        distinct_ips = evt.get("distinct_ips")
        alert = {"id": pid, "agent": self.id, "type": "network_fastflux", "uid": uid,
                   "distinct_ips": distinct_ips, "ts": int(time.time())}

        if sign_and_append(alert):
            logger.info(f"[agent-{self.id}] Network spike {distinct_ips} ips")
            self.app.add_alert(alert) # update GUI
        else:
            logger.error(f"[agent-{self.id}] Could not sign alert")

    async def handle_generic_event(self, evt: Dict[str, Any]):
        pid = secrets.token_hex(8)
        alert = {"id": pid, "agent": self.id, "type": "generic", "raw": evt, "ts": int(time.time())}

        if sign_and_append(alert):
            self.app.add_alert(alert) # update GUI
            logger.info(f"[agent-{self.id}] Logged generic event")
        else:
            logger.error(f"[agent-{self.id}] Could not sign alert")

# ---- file watcher to convert FS events into swarm events ----
class ApkWatchHandler(FileSystemEventHandler):
    """A watchdog event handler that puts new APK file events into the event queue"""
    def __init__(self, q: Queue):
        self.q = q

    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith(".apk"):
            self.q.put({"type": "apk_new", "path": event.src_path})
            logger.info(f"Detected new APK: {event.src_path}")

# ---- Textual UI ----
class SwarmApp(App):
    """Textual UI for the Swarm"""

    CSS_PATH = "swarm.css"  # Create this file (see below)
    BINDINGS = [("q", "quit", "Quit"), ("d", "toggle_dark", "Toggle Dark Mode")]

    alerts = reactive([]) # Reactive list of alerts
    dark = reactive(True) # reactive bool

    def compose(self) -> ComposeResult:
        """Compose the UI"""
        yield Header(show_clock=True)
        with Vertical():
            yield Static("Swarm Status:", id="status")
            yield DataTable(id="alerts_table")
            yield Static("Swarm log:", id="log")
        yield Footer()

    def on_mount(self) -> None:
        """When app is mounted, populate table"""
        self.update_table()
        self.set_interval(5, self.watch_log) # update swarm log every 5 seconds

    def add_alert(self, alert):
        """Add an alert to the list and update the table."""
        self.alerts = [alert] + self.alerts
        self.update_table()

    def watch_log(self) -> None:
        """Read recent swarm logs and add to UI"""
        with open(INC_DIR / "incidents.jsonl", "r") as f:
            lines = f.readlines()
        data_block = "".join(lines[-5:]) # Get last 5 alerts
        self.query_one("#log", Static).update(Markdown(f"### Recent Swarm Logs: \n {data_block}")) # Update Logs UI
    def update_table(self) -> None:
        """Update the contents of the table."""
        table = self.query_one("#alerts_table", DataTable)
        table.clear()
        table.add_column("ID")
        table.add_column("Agent")
        table.add_column("Type")
        table.add_column("Details")

        for alert in self.alerts:
            table.add_row(
                alert["id"],
                str(alert["agent"]),
                alert["type"],
                str(alert.get("yara_matches") or alert.get("path") or alert.get("distinct_ips") or alert.get("raw")) # details
            )

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Called when a table row is selected."""
        table = self.query_one("#alerts_table", DataTable)
        row_key = event.row_key
        row = table.get_row(row_key)
        logger.info(f"Selected Row: {row} / Key {row_key}") # Alert for debugging purposes

    def action_toggle_dark(self) -> None:
        """Toggle dark mode."""
        self.dark = not self.dark

# ---- main ----
def main():
    """Main function"""
    num_agents = NUM_AGENTS
    q = Queue()

    if TEXTUAL_AVAILABLE:
      app = SwarmApp()
      agents = [Agent(i, q, app) for i in range(num_agents)] # Pass the app
      for a in agents:
          a.start()

      # watch home Download and /sdcard/Download if present
      observer = Observer()
      handler = ApkWatchHandler(q)

      # Dynamically add and validate watch directories
      valid_watch_dirs = []
      for d in [dir.strip() for dir in WATCH_DIRECTORIES]:
          if os.path.isdir(d):
              valid_watch_dirs.append(d)
              observer.schedule(handler, d, recursive=False)
              logger.info(f"[watch] Watching directory: {d}")
          else:
              logger.warning(f"[watch] Directory not found: {d}")

      if not valid_watch_dirs:
          logger.warning("[watch] No valid watch directories found.")

      observer.start()

      # stdin loop for simulated events
      logger.info("Swarm simulator running. Listening to stdin for new JSON events.")
      try:
          app.run()
      except KeyboardInterrupt:
          logger.info("Exiting swarm simulator.")
      finally:
          observer.stop()
          observer.join()
          for agent in agents:
              agent.executor.shutdown(wait=False)

    else:
        print("Textual UI not available. Run `pip install textual`")

if __name__ == "__main__":
    main()
