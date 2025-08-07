"""Module for interacting with Synology Router API."""

from .api_utils import ConfigManager
from .client import Client
from .wifi_utils import WiFiConfigManager

__all__ = [
    "Client",
    "ConfigManager",
    "NetworkType",
    "RadioType",
    "SecurityLevel",
    "WiFiConfigManager",
    "WiFiUtils",
]
