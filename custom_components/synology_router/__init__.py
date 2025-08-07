"""The Synology SRM integration."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
    Platform,
)
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    ATTR_NETWORK_NAME,
    ATTR_PROFILE_ID,
    ATTR_RADIO_TYPE,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    SERVICE_DISABLE_WIFI,
    SERVICE_ENABLE_WIFI,
    SERVICE_TOGGLE_SMART_CONNECT,
)
from .synology_api import Client, WiFiConfigManager

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SWITCH]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Synology SRM from a config entry."""
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    def create_client():
        return Client(
            host=host,
            port=port,
            username=username,
            password=password,
            https=False,
        )

    try:
        client = await hass.async_add_executor_job(create_client)
        await hass.async_add_executor_job(client.base.query_info)
    except Exception as err:
        _LOGGER.error("Failed to connect to Synology SRM: %s", err)
        raise ConfigEntryNotReady from err

    coordinator = SynologySRMDataUpdateCoordinator(hass, client, scan_interval)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    await _async_register_services(hass)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

        if not hass.data[DOMAIN]:
            for service in [
                SERVICE_ENABLE_WIFI,
                SERVICE_DISABLE_WIFI,
                SERVICE_TOGGLE_SMART_CONNECT,
            ]:
                hass.services.async_remove(DOMAIN, service)

    return unload_ok


class SynologySRMDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Synology SRM."""

    def __init__(self, hass: HomeAssistant, client: Client, scan_interval: int) -> None:
        """Initialize."""
        self.client = client

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            wifi_config = await self.hass.async_add_executor_job(
                self.client.get_wifi_network_setting
            )

        except (OSError, ValueError, TypeError, AttributeError) as err:
            _LOGGER.error("Error communicating with Synology SRM: %s", err)
            raise UpdateFailed(f"Error communicating with Synology SRM: {err}") from err
        else:
            return {"wifi_config": wifi_config}


def _enable_network_by_name(manager, network_name):
    """Enable network by SSID name."""
    for profile in manager.get_profiles():
        for radio in profile.get("radio_list", []):
            if radio.get("ssid") == network_name:
                if manager.is_radio_available(profile["id"], radio["radio_type"]):
                    manager.enable_radio(profile["id"], radio["radio_type"], True)
                    return True
    return False


def _disable_network_by_name(manager, network_name):
    """Disable network by SSID name."""
    for profile in manager.get_profiles():
        for radio in profile.get("radio_list", []):
            if radio.get("ssid") == network_name:
                if manager.is_radio_available(profile["id"], radio["radio_type"]):
                    manager.enable_radio(profile["id"], radio["radio_type"], False)
                    return True
    return False


async def _async_register_services(hass: HomeAssistant) -> None:
    """Register services for the integration."""

    async def async_enable_wifi(call: ServiceCall):
        """Service to enable WiFi network."""
        profile_id = call.data.get(ATTR_PROFILE_ID)
        radio_type = call.data.get(ATTR_RADIO_TYPE)
        network_name = call.data.get(ATTR_NETWORK_NAME)

        for coordinator in hass.data[DOMAIN].values():
            try:

                def enable_network(coord=coordinator):
                    config = coord.client.get_wifi_network_setting()
                    manager = WiFiConfigManager(config)

                    if network_name:
                        if not _enable_network_by_name(manager, network_name):
                            return False
                    elif profile_id is not None and radio_type:
                        if not manager.is_radio_available(profile_id, radio_type):
                            return False
                        manager.enable_radio(profile_id, radio_type, True)
                    else:
                        return False

                    return coord.client.set_wifi_network_setting(manager.get_config())

                await hass.async_add_executor_job(enable_network)
                await coordinator.async_request_refresh()

            except (OSError, ValueError, TypeError, KeyError) as err:
                _LOGGER.error("Failed to enable WiFi: %s", err)

    async def async_disable_wifi(call: ServiceCall):
        """Service to disable WiFi network."""
        profile_id = call.data.get(ATTR_PROFILE_ID)
        radio_type = call.data.get(ATTR_RADIO_TYPE)
        network_name = call.data.get(ATTR_NETWORK_NAME)

        for coordinator in hass.data[DOMAIN].values():
            try:

                def disable_network(coord=coordinator):
                    config = coord.client.get_wifi_network_setting()
                    manager = WiFiConfigManager(config)

                    if network_name:
                        if not _disable_network_by_name(manager, network_name):
                            return False
                    elif profile_id is not None and radio_type:
                        if not manager.is_radio_available(profile_id, radio_type):
                            return False
                        manager.enable_radio(profile_id, radio_type, False)
                    else:
                        return False

                    return coord.client.set_wifi_network_setting(manager.get_config())

                await hass.async_add_executor_job(disable_network)
                await coordinator.async_request_refresh()

            except (OSError, ValueError, TypeError, KeyError) as err:
                _LOGGER.error("Failed to disable WiFi: %s", err)

    async def async_toggle_smart_connect(call: ServiceCall):
        """Service to toggle Smart Connect mode."""
        profile_id = call.data.get(ATTR_PROFILE_ID)
        enable = call.data.get("enable", True)

        if profile_id is None:
            return

        for coordinator in hass.data[DOMAIN].values():
            try:

                def toggle_smart_connect(coord=coordinator):
                    config = coord.client.get_wifi_network_setting()
                    manager = WiFiConfigManager(config)
                    manager.toggle_smart_connect(profile_id, enable)
                    return coord.client.set_wifi_network_setting(manager.get_config())

                await hass.async_add_executor_job(toggle_smart_connect)
                await coordinator.async_request_refresh()

            except (OSError, ValueError, TypeError) as err:
                _LOGGER.error("Failed to toggle Smart Connect: %s", err)

    hass.services.async_register(DOMAIN, SERVICE_ENABLE_WIFI, async_enable_wifi)
    hass.services.async_register(DOMAIN, SERVICE_DISABLE_WIFI, async_disable_wifi)
    hass.services.async_register(
        DOMAIN, SERVICE_TOGGLE_SMART_CONNECT, async_toggle_smart_connect
    )
