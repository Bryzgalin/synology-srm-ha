"""Switch platform for Synology SRM integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .synology_api import WiFiConfigManager

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Synology SRM switch entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = []

    if not isinstance(coordinator.data, dict):
        return

    wifi_config = coordinator.data.get("wifi_config")
    if wifi_config:
        try:
            manager = WiFiConfigManager(wifi_config)
            networks = manager.get_network_summary()

            for network in networks:
                if network["switch_type"] == "smart_connect_toggle":
                    entities.append(
                        SynologySmartConnectToggleSwitch(
                            coordinator=coordinator,
                            profile_id=network["profile_id"],
                            profile_name=network["profile_name"],
                            network_type=network["network_type"],
                        )
                    )
                elif network["switch_type"] == "radio":
                    entities.append(
                        SynologyWiFiRadioSwitch(
                            coordinator=coordinator,
                            profile_id=network["profile_id"],
                            radio_type=network["radio_type"],
                            ssid=network["ssid"],
                            network_type=network["network_type"],
                            profile_name=network["profile_name"],
                        )
                    )

        except (KeyError, ValueError, TypeError) as err:
            _LOGGER.error("Invalid WiFi configuration data: %s", err)

    if entities:
        async_add_entities(entities)


class SynologySmartConnectToggleSwitch(CoordinatorEntity, SwitchEntity):
    """Switch for toggling Smart Connect mode for a profile."""

    def __init__(
        self,
        coordinator,
        profile_id: int,
        profile_name: str,
        network_type: str,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._profile_id = profile_id
        self._profile_name = profile_name
        self._network_type = network_type

        self._attr_unique_id = (
            f"{coordinator.client.http.host}_{profile_id}_smart_connect_toggle"
        )
        self._attr_name = f"{profile_name} - SmartConnect Toggle"
        self._attr_icon = "mdi:wifi-settings"

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            isinstance(self.coordinator.data, dict)
            and "wifi_config" in self.coordinator.data
            and self.coordinator.last_update_success
        )

    @property
    def is_on(self) -> bool:
        """Return true if Smart Connect is enabled."""
        if not self.available:
            return False

        try:
            wifi_config = self.coordinator.data.get("wifi_config")
            if wifi_config:
                manager = WiFiConfigManager(wifi_config)
                return manager.is_smart_connect_enabled(self._profile_id)
        except (KeyError, ValueError, TypeError, AttributeError):
            pass

        return False

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        return {
            "profile_id": self._profile_id,
            "network_type": self._network_type,
            "switch_type": "smart_connect_toggle",
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable Smart Connect for this profile."""
        try:

            def enable_smart_connect():
                config = self.coordinator.client.get_wifi_network_setting()
                manager = WiFiConfigManager(config)
                manager.toggle_smart_connect(self._profile_id, True)
                return self.coordinator.client.set_wifi_network_setting(
                    manager.get_config()
                )

            await self.hass.async_add_executor_job(enable_smart_connect)
            await self.coordinator.async_request_refresh()

        except (OSError, ValueError, TypeError) as err:
            _LOGGER.error("Failed to enable Smart Connect: %s", err)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable Smart Connect for this profile."""
        try:

            def disable_smart_connect():
                config = self.coordinator.client.get_wifi_network_setting()
                manager = WiFiConfigManager(config)
                manager.toggle_smart_connect(self._profile_id, False)
                return self.coordinator.client.set_wifi_network_setting(
                    manager.get_config()
                )

            await self.hass.async_add_executor_job(disable_smart_connect)
            await self.coordinator.async_request_refresh()

        except (OSError, ValueError, TypeError) as err:
            _LOGGER.error("Failed to disable Smart Connect: %s", err)


class SynologyWiFiRadioSwitch(CoordinatorEntity, SwitchEntity):
    """Switch for individual WiFi radio control."""

    def __init__(
        self,
        coordinator,
        profile_id: int,
        radio_type: str,
        ssid: str,
        network_type: str,
        profile_name: str,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._profile_id = profile_id
        self._radio_type = radio_type
        self._ssid = ssid
        self._network_type = network_type
        self._profile_name = profile_name

        self._attr_unique_id = (
            f"{coordinator.client.http.host}_{profile_id}_{radio_type}"
        )
        self._attr_name = f"{profile_name} - {ssid} ({radio_type})"

        if radio_type == "SmartConnect":
            self._attr_icon = "mdi:wifi-star"
        else:
            self._attr_icon = "mdi:wifi"

    @property
    def available(self) -> bool:
        """Return if entity is available for control."""
        if not (
            isinstance(self.coordinator.data, dict)
            and "wifi_config" in self.coordinator.data
            and self.coordinator.last_update_success
        ):
            return False

        try:
            wifi_config = self.coordinator.data.get("wifi_config")
            if wifi_config:
                manager = WiFiConfigManager(wifi_config)
                return manager.is_radio_available(self._profile_id, self._radio_type)
        except (KeyError, ValueError, TypeError, AttributeError):
            pass

        return False

    @property
    def is_on(self) -> bool:
        """Return true if the radio is enabled."""
        if not isinstance(self.coordinator.data, dict):
            return False

        try:
            wifi_config = self.coordinator.data.get("wifi_config")
            if wifi_config:
                manager = WiFiConfigManager(wifi_config)
                return manager.is_radio_enabled(self._profile_id, self._radio_type)
        except (KeyError, ValueError, TypeError, AttributeError):
            pass

        return False

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attributes = {
            "profile_id": self._profile_id,
            "radio_type": self._radio_type,
            "network_type": self._network_type,
            "ssid": self._ssid,
            "switch_type": "radio",
        }

        try:
            wifi_config = self.coordinator.data.get("wifi_config")
            if wifi_config:
                manager = WiFiConfigManager(wifi_config)
                attributes["smart_connect_enabled"] = manager.is_smart_connect_enabled(
                    self._profile_id
                )
                attributes["radio_available"] = manager.is_radio_available(
                    self._profile_id, self._radio_type
                )

                radio = manager.get_radio_by_type(self._profile_id, self._radio_type)
                if radio:
                    attributes.update(
                        {
                            "hidden": radio.get("hide_ssid", False),
                            "security_level": radio.get("security", {}).get(
                                "security_level"
                            ),
                            "max_connections": radio.get("max_connection", 0),
                            "client_isolation": radio.get(
                                "enable_client_isolation", False
                            ),
                        }
                    )
        except (KeyError, ValueError, TypeError, AttributeError):
            pass

        return attributes

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the radio on."""
        try:

            def enable_radio():
                config = self.coordinator.client.get_wifi_network_setting()
                manager = WiFiConfigManager(config)
                manager.enable_radio(self._profile_id, self._radio_type, True)
                return self.coordinator.client.set_wifi_network_setting(
                    manager.get_config()
                )

            await self.hass.async_add_executor_job(enable_radio)
            await self.coordinator.async_request_refresh()

        except (OSError, ValueError, TypeError) as err:
            _LOGGER.error("Failed to enable radio: %s", err)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the radio off."""
        try:

            def disable_radio():
                config = self.coordinator.client.get_wifi_network_setting()
                manager = WiFiConfigManager(config)
                manager.enable_radio(self._profile_id, self._radio_type, False)
                return self.coordinator.client.set_wifi_network_setting(
                    manager.get_config()
                )

            await self.hass.async_add_executor_job(disable_radio)
            await self.coordinator.async_request_refresh()

        except (OSError, ValueError, TypeError) as err:
            _LOGGER.error("Failed to disable radio: %s", err)
