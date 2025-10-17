"""
BLUX Guard Rules Engine Configuration Package

This package manages the loading, validation, and application of security rules
within the BLUX Guard ecosystem. It provides tools for dynamically updating
rulesets and handling any associated dependencies.

Version: 1.0.0
Author: Outer Void Team
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Default rules directory (relative to /blux-guard, adjust as needed)
DEFAULT_RULES_DIR = Path("/blux-guard/.config/rules")
DEFAULT_RULES_FILE = DEFAULT_RULES_DIR / "rules.json"

class RulesEngineConfig:
    """
    Configuration class for the BLUX Guard Rules Engine.
    Manages the loading and validation of security rules from JSON files.
    """

    def __init__(self, rules_dir: Optional[Path] = None, rules_file: Optional[Path] = None):
        """
        Initializes the RulesEngineConfig with the specified rules directory
        and rules file. If not provided, defaults are used.
        """
        self.rules_dir = rules_dir or DEFAULT_RULES_DIR
        self.rules_file = rules_file or DEFAULT_RULES_FILE
        self.rules = self._load_and_validate_rules()


    def _load_and_validate_rules(self) -> List[Dict[str, Any]]:
        """
        Loads the rules from the configured JSON file and validates
        their structure. Returns a list of rule dictionaries.
        Raises an exception if the file is invalid or rules are malformed.
        """
        try:
            with open(self.rules_file, 'r') as f:
                data = json.load(f)

            if not isinstance(data, dict) or 'rules' not in data:
                raise ValueError("Invalid rules file format: 'rules' key missing.")

            rules = data['rules']
            if not isinstance(rules, list):
                raise ValueError("Invalid rules file format: 'rules' must be a list.")

            # Perform basic rule validation (add more checks as needed)
            for rule in rules:
                if not isinstance(rule, dict):
                    raise ValueError("Invalid rule format: Each rule must be a dictionary.")
                if 'id' not in rule or 'condition' not in rule or 'response' not in rule:
                     raise ValueError(f"Rule with ID '{rule.get('id', 'unknown')}' is missing required fields ('id', 'condition', 'response').")

            logger.info(f"Successfully loaded and validated {len(rules)} rules from {self.rules_file}")
            return rules

        except FileNotFoundError:
            logger.error(f"Rules file not found: {self.rules_file}")
            raise  # Re-raise to indicate configuration error
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON in {self.rules_file}: {e}")
            raise  # Re-raise to indicate configuration error
        except ValueError as e:
            logger.error(f"Validation error in rules file: {e}")
            raise  # Re-raise to indicate configuration error
        except Exception as e:
            logger.exception(f"Unexpected error loading rules: {e}")
            raise  # Re-raise to indicate configuration error


    def get_rules(self) -> List[Dict[str, Any]]:
        """
        Returns the list of loaded and validated rules.
        """
        return self.rules

    def reload_rules(self):
        """
        Reloads the rules from the configuration file.
        Useful for dynamically updating rulesets.
        """
        try:
            self.rules = self._load_and_validate_rules()
            logger.info("Rules reloaded successfully.")
        except Exception as e:
            logger.error(f"Failed to reload rules: {e}")

# Example usage and initialization (optional)
try:
    rules_config = RulesEngineConfig()
    all_rules = rules_config.get_rules()
    logger.info(f"RulesEngineConfig initialized with {len(all_rules)} rules.")
except Exception as e:
    logger.error(f"Failed to initialize RulesEngineConfig: {e}")

# Define __all__ for public API exposure
__all__ = [
    "RulesEngineConfig",
    "DEFAULT_RULES_DIR",
    "DEFAULT_RULES_FILE",
    "logger",
    "all_rules" if 'all_rules' in locals() else None  # Only expose if initialized
]
