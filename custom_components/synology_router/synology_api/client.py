"""Client for Synology SRM API."""

from .api.base import ApiBase
from .api.core import ApiCore
from .api.mesh import ApiMesh
from .api.wifi import ApiWifi
from .http import Http


class Client:
    """Client to interact with Synology SRM API."""

    def __init__(
        self, host: str, port: int, username: str, password: str, https: bool = True
    ) -> None:
        """Initialize the Synology SRM API client."""

        self.http = Http(
            host=host,
            port=port,
            username=username,
            password=password,
            https=https,
        )

        self.api = {
            "base": ApiBase(self.http),
            "core": ApiCore(self.http),
            "mesh": ApiMesh(self.http),
            "wifi": ApiWifi(self.http),
        }

    def __getattr__(self, item) -> None:
        """Get API methods dynamically."""
        return self.api[item]

    # Convenience methods for WiFi operations
    def get_wifi_network_setting(self):
        """Get WiFi network settings.

        Returns:
            dict: Complete WiFi configuration
        """
        return self.wifi.get_network_setting()

    def set_wifi_network_setting(self, config):
        """Set WiFi network settings.

        Args:
            config: WiFi configuration (can be dict or profiles list)

        Returns:
            dict: API response
        """
        return self.wifi.set_network_setting(config)

    def get_wifi_connected_devices(self, filters=None):
        """Get connected WiFi devices.

        Args:
            filters: Optional filters to apply

        Returns:
            list: List of connected devices
        """
        return self.wifi.get_connected_devices(filters or {})

    def get_wifi_radio_status(self):
        """Get WiFi radio status.

        Returns:
            list: List of radio status information
        """
        return self.wifi.get_radio_status()

    def disconnect_wifi_device(self, mac_address):
        """Disconnect a WiFi device.

        Args:
            mac_address: MAC address of device to disconnect

        Returns:
            bool: True if successful
        """
        response = self.wifi.disconnect_device(mac_address)
        return response.get("success", False)

    def block_wifi_device(self, mac_address):
        """Block a WiFi device.

        Args:
            mac_address: MAC address of device to block

        Returns:
            bool: True if successful
        """
        response = self.wifi.block_device(mac_address)
        return response.get("success", False)

    def unblock_wifi_device(self, mac_address):
        """Unblock a WiFi device.

        Args:
            mac_address: MAC address of device to unblock

        Returns:
            bool: True if successful
        """
        response = self.wifi.unblock_device(mac_address)
        return response.get("success", False)

    def start_wps(self):
        """Start WPS Push Button Configuration.

        Returns:
            bool: True if started successfully
        """
        response = self.wifi.start_wps_pbc()
        return response.get("success", False)

    def stop_wps(self):
        """Stop WPS operation.

        Returns:
            bool: True if stopped successfully
        """
        response = self.wifi.stop_wps()
        return response.get("success", False)

    def get_wps_status(self):
        """Get WPS status.

        Returns:
            dict: WPS status information
        """
        return self.wifi.get_wps_status()

    def scan_wifi_networks(self, radio_type="2.4G"):
        """Scan for WiFi networks.

        Args:
            radio_type: Radio type to scan with

        Returns:
            list: List of found networks
        """
        # Start scan
        self.wifi.start_wifi_scan(radio_type)
        # Get results (in real usage, you might want to wait a bit)
        return self.wifi.get_wifi_scan_results(radio_type)

    def set_wifi_channel(self, radio_type, channel):
        """Set WiFi channel for a radio.

        Args:
            radio_type: Radio type (2.4G, 5G-1, 5G-2)
            channel: Channel number

        Returns:
            bool: True if successful
        """
        response = self.wifi.set_radio_channel(radio_type, channel)
        return response.get("success", False)

    def set_wifi_power(self, radio_type, power):
        """Set WiFi transmission power.

        Args:
            radio_type: Radio type (2.4G, 5G-1, 5G-2)
            power: Power percentage (0-100)

        Returns:
            bool: True if successful
        """
        response = self.wifi.set_radio_power(radio_type, power)
        return response.get("success", False)

    def get_wifi_country_code(self):
        """Get current WiFi country code.

        Returns:
            str: Current country code
        """
        return self.wifi.get_current_country_code()

    def set_wifi_country_code(self, country_code):
        """Set WiFi country code.

        Args:
            country_code: Country code (e.g., 'UA', 'US', 'EU')

        Returns:
            bool: True if successful
        """
        response = self.wifi.set_country_code(country_code)
        return response.get("success", False)
