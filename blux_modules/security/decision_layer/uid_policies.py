#!/usr/bin/env python3
"""
BLUX Guard — UID Policy Definitions
- Per-UID policies: whitelist / greylist / blacklist
- Used by decision_engine.py
"""
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define default policy
DEFAULT_POLICY = "greylist"

def load_uid_policies(policy_file: str = None) -> dict:
    """Loads UID policies from a file (JSON or plain text).

    Args:
        policy_file: Path to the policy file. If None, uses the default policies.

    Returns:
        A dictionary containing UID policies.
    """
    if policy_file and os.path.exists(policy_file):
        try:
            if policy_file.endswith(".json"):
                import json
                with open(policy_file, "r") as f:
                    policies = json.load(f)
                logger.info(f"Loaded UID policies from JSON file: {policy_file}")
                return policies
            else:  # Assume plain text file (one UID=policy per line)
                policies = {}
                with open(policy_file, "r") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):  # Skip comments and empty lines
                            continue
                        try:
                            uid, policy = line.split("=", 1)
                            uid = uid.strip()
                            policy = policy.strip()
                            policies[uid] = policy
                        except ValueError:
                            logger.warning(f"Invalid policy line in {policy_file}: {line}")
                logger.info(f"Loaded UID policies from text file: {policy_file}")
                return policies
        except Exception as e:
            logger.error(f"Error loading UID policies from {policy_file}: {e}")
            return {}  # Return empty dict on error to avoid crashes
    else:
        logger.info("Using default UID policies.")
        # Default UID Policies - hardcoded
        policies = {
            # Whitelisted UIDs — safe, minimal monitoring
            "com.example.good": "whitelist",
            "com.example.trusted": "whitelist",

            # Greylisted UIDs — monitor, escalate based on severity
            "com.example.suspicious": "greylist",
            "com.example.unverified": "greylist",

            # Blacklisted UIDs — immediate lockdown/quarantine
            "com.example.malware": "blacklist",
            "com.example.spyware": "blacklist"
        }
        return policies

def get_policy(uid: str, policy_file: str = None) -> str:
    """Return policy for a given UID. Default: greylist"""
    policies = load_uid_policies(policy_file)
    return policies.get(uid, DEFAULT_POLICY)

if __name__ == "__main__":
    # Example Usage
    policy = get_policy("com.example.malware")
    print(f"Policy for com.example.malware: {policy}")
    policy = get_policy("com.example.unknown")
    print(f"Policy for com.example.unknown: {policy}")

    # Load from file
    policy = get_policy("com.example.new", policy_file="policies.txt") # Create example
    print(f"Policy for file import: {policy}")
