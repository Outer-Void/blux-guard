"""
scripts Package
===============

This package contains utility scripts (both Python and shell) for the BLUX Guard project.
"""

import os
import subprocess

__all__ = [
    'run_guard',
    'setup_env',
    'create_venv',
    'setup_security'
]


def run_script(script_name: str, *args):
    """
    Executes a shell script or a Python script within the scripts directory.

    Args:
        script_name (str): The name of the script (without the extension).
        *args: Arguments to pass to the script.

    Raises:
        FileNotFoundError: If the script does not exist.
        subprocess.CalledProcessError: If the script exits with a non-zero code.
    """
    script_path = os.path.join(os.path.dirname(__file__), f"{script_name}")
    python_script_path = script_path + ".py"
    shell_script_path = script_path + ".sh"

    if os.path.exists(python_script_path):
        try:
            subprocess.run(["python3", python_script_path, *args], check=True)
        except FileNotFoundError:
            try:
               subprocess.run(["python", python_script_path, *args], check=True)
            except:
                raise FileNotFoundError(f"Python not found.")
        except subprocess.CalledProcessError as e:
            print(f"Error running Python script {script_name}: {e}")
            raise
    elif os.path.exists(shell_script_path):
        try:
            subprocess.run(["bash", shell_script_path, *args], check=True)
        except FileNotFoundError:
            raise FileNotFoundError(f"Bash not found.")
        except subprocess.CalledProcessError as e:
            print(f"Error running shell script {script_name}: {e}")
            raise
    else:
        raise FileNotFoundError(f"Script '{script_name}' not found in scripts directory.")


def run_guard(*args):
    """Runs the run_guard.sh script."""
    run_script('run_guard', *args)


def setup_env(*args):
    """Runs the setup_env.sh script."""
    run_script('setup_env', *args)


def create_venv(*args):
    """Runs the create_venv.sh script."""
    run_script('create_venv', *args)


def setup_security(*args):
    """Runs the setup_security.py script."""
    run_script('setup_security', *args)
