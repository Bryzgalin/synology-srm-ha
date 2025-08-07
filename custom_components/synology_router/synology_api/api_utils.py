"""API utilities for Synology SRM API."""

import json
from pathlib import Path
from typing import Any


class ConfigManager:
    """Helper class for managing API configurations."""

    def __init__(self, save_location: str = "./") -> None:
        """Initialize the ConfigManager."""

        self.save_location = save_location
        Path("save_location").mkdir(parents=True)

    def save_config_to_disk(self, config: dict[str, Any], filepath: str) -> bool:
        """Save configuration to disk.

        Args:
            config: SRM configuration received from API
            filepath: File path to save to

        Returns:
            bool: True if saved successfully
        """
        filepath = Path.joinpath(self.save_location, filepath)
        try:
            with Path.open(filepath, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except OSError:
            return False
        except (json.JSONEncodeError, UnicodeError):
            return False
        else:
            return True

    def load_config_from_disk(self, filepath: str) -> dict[str, Any]:
        """Load configuration from disk.

        Args:
            filepath: File path to load from

        Returns:
            dict: SRM configuration

        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is not valid JSON
        """
        with Path.open(filepath, encoding="utf-8") as f:
            return json.load(f)
