"""WiFi configuration utilities for Synology SRM."""

import logging
from typing import Any

_LOGGER = logging.getLogger(__name__)


class WiFiConfigManager:
    """Manager for WiFi configuration."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize with WiFi configuration."""
        self.config = config

    def get_profiles(self) -> list[dict[str, Any]]:
        """Get all WiFi profiles."""
        return self.config.get("profiles", [])

    def get_profile_by_id(self, profile_id: int) -> dict[str, Any] | None:
        """Get profile by ID."""
        for profile in self.get_profiles():
            if profile.get("id") == profile_id:
                return profile
        return None

    def get_radio_by_type(
        self, profile_id: int, radio_type: str
    ) -> dict[str, Any] | None:
        """Get radio configuration by profile ID and radio type."""
        profile = self.get_profile_by_id(profile_id)
        if not profile:
            return None

        for radio in profile.get("radio_list", []):
            if radio.get("radio_type") == radio_type:
                return radio
        return None

    def get_network_summary(self) -> list[dict[str, Any]]:
        """Get summary of all networks for creating switches."""
        networks = []

        for profile in self.get_profiles():
            profile_id = profile.get("id")
            profile_name = profile.get("name", f"Profile {profile_id}")
            network_type = profile.get("network_type", "custom")
            enable_smart_connect = profile.get("enable_smart_connect", False)

            # Додаємо switch для керування Smart Connect режимом
            networks.append(
                {
                    "profile_id": profile_id,
                    "radio_type": "smart_connect_toggle",
                    "ssid": " SmartConnect Toggle",
                    "network_type": network_type,
                    "profile_name": profile_name,
                    "switch_type": "smart_connect_toggle",
                    "enabled": enable_smart_connect,
                    "always_available": True,
                }
            )

            # Додаємо switches для всіх радіо
            for radio in profile.get("radio_list", []):
                radio_type = radio.get("radio_type")
                ssid = radio.get("ssid", f"Unknown_{radio_type}")
                enabled = radio.get("enable", False)

                # Визначаємо доступність based on Smart Connect
                if radio_type == "SmartConnect":
                    available = enable_smart_connect
                else:  # 2.4G, 5G-1, 5G-2
                    available = not enable_smart_connect

                networks.append(
                    {
                        "profile_id": profile_id,
                        "radio_type": radio_type,
                        "ssid": ssid,
                        "network_type": network_type,
                        "profile_name": profile_name,
                        "switch_type": "radio",
                        "enabled": enabled,
                        "available": available,
                        "always_available": False,
                    }
                )

        return networks

    def toggle_smart_connect(self, profile_id: int, enable: bool) -> bool:
        """Toggle Smart Connect for a profile."""
        profile = self.get_profile_by_id(profile_id)
        if not profile:
            _LOGGER.error("Profile %s not found", profile_id)
            return False

        # Змінюємо enable_smart_connect
        profile["enable_smart_connect"] = enable

        _LOGGER.info("Smart Connect for profile %s set to %s", profile_id, enable)
        return True

    def enable_radio(self, profile_id: int, radio_type: str, enable: bool) -> bool:
        """Enable/disable specific radio."""
        radio = self.get_radio_by_type(profile_id, radio_type)
        if not radio:
            _LOGGER.error("Radio %s in profile %s not found", radio_type, profile_id)
            return False

        radio["enable"] = enable
        _LOGGER.info("Radio %s in profile %s set to %s", radio_type, profile_id, enable)
        return True

    def get_config(self) -> dict[str, Any]:
        """Get the current configuration."""
        return self.config

    def is_smart_connect_enabled(self, profile_id: int) -> bool:
        """Check if Smart Connect is enabled for profile."""
        profile = self.get_profile_by_id(profile_id)
        return profile.get("enable_smart_connect", False) if profile else False

    def is_radio_available(self, profile_id: int, radio_type: str) -> bool:
        """Check if radio is available for control."""
        profile = self.get_profile_by_id(profile_id)
        if not profile:
            return False

        enable_smart_connect = profile.get("enable_smart_connect", False)

        if radio_type == "SmartConnect":
            return enable_smart_connect
        # 2.4G, 5G-1, 5G-2
        return not enable_smart_connect

    def is_radio_enabled(self, profile_id: int, radio_type: str) -> bool:
        """Check if radio is enabled."""
        radio = self.get_radio_by_type(profile_id, radio_type)
        return radio.get("enable", False) if radio else False
