"""WiFi API for Synology SRM."""

import json

from ..api import Api


class ApiWifi(Api):
    """API WiFi.

    Handles the SYNO.Wifi API namespace for WiFi network management.
    """

    def get_network_setting(self):
        """Get WiFi network settings.

        Returns:
            dict: WiFi network configuration including all profiles and radio settings
        """
        return self.http.call(
            endpoint="entry.cgi",
            api="SYNO.Wifi.Network.Setting",
            method="get",
            version=1,
        )

    def set_network_setting(self, profiles):
        """Set WiFi network settings.

        Args:
            profiles: List of WiFi profile configurations or complete config dict

        Returns:
            dict: API response
        """
        # Handle both formats: profiles list or complete config dict
        if isinstance(profiles, dict) and "profiles" in profiles:
            profiles_data = profiles["profiles"]
        elif isinstance(profiles, list):
            profiles_data = profiles
        else:
            raise ValueError("Profiles must be a list or dict with 'profiles' key")

        return self.http.call(
            endpoint="entry.cgi",
            api="SYNO.Wifi.Network.Setting",
            method="set",
            version=1,
            params={"profiles": json.dumps(profiles_data)},
        )

    def get_connected_devices(self, filters=None):
        """Get list of connected WiFi devices.

        Args:
            filters: Optional filters to apply (compatible with existing _filter method)

        Returns:
            list: List of connected devices with their information
        """
        response = self.http.call(
            endpoint="entry.cgi",
            api="SYNO.Wifi.Device",
            method="get",
            version=1,
        )

        return self._filter(response.get("device_list", []), filters or {})

    def disconnect_device(self, mac_address):
        """Disconnect a WiFi device by MAC address.

        Args:
            mac_address: MAC address of the device to disconnect

        Returns:
            dict: API response
        """
        return self.http.call(
            endpoint="entry.cgi",
            api="SYNO.Wifi.Device",
            method="get",
            version=1,
            params={"mac": mac_address},
        )

    def block_device(self, mac_address):
        """Block a WiFi device by MAC address.

        Args:
            mac_address: MAC address of the device to block

        Returns:
            dict: API response
        """
        return self.http.call(
            endpoint="entry.cgi",
            api="SYNO.Wifi.Device",
            method="get",
            version=1,
            params={"mac": mac_address},
        )

    def unblock_device(self, mac_address):
        """Unblock a WiFi device by MAC address.

        Args:
            mac_address: MAC address of the device to unblock

        Returns:
            dict: API response
        """
        return self.http.call(
            endpoint="entry.cgi",
            api="SYNO.Wifi.Device",
            method="get",
            version=1,
            params={"mac": mac_address},
        )

    def get_radio_status(self):
        """Get WiFi radio status for all bands.

        Returns:
            list: Radio status information for all WiFi bands
        """
        response = self.http.call(
            endpoint="entry.cgi",
            api="SYNO.Wifi.Radio.Status",
            method="get",
            version=1,
        )
        return response.get("status_list", [])

    def get_radio_capability(self):
        """Get WiFi radio capabilities.

        Returns:
            dict: Radio capabilities including supported channels, standards, etc.
        """
        return self.http.call(
            endpoint="entry.cgi",
            api="SYNO.Wifi.Radio.Capability",
            method="get",
            version=1,
        )

    def set_radio_channel(self, radio_type, channel):
        """Set WiFi radio channel.

        Args:
            radio_type: Radio type (2.4G, 5G-1, 5G-2)
            channel: Channel number to set

        Returns:
            dict: API response
        """
        return self.http.call(
            endpoint="entry.cgi",
            api="SYNO.Wifi.Radio.Setting",
            method="get",
            version=1,
            params={"radio_type": radio_type, "channel": channel},
        )

    def set_radio_power(self, radio_type, tx_power):
        """Set WiFi radio transmission power.

        Args:
            radio_type: Radio type (2.4G, 5G-1, 5G-2)
            tx_power: Transmission power percentage (0-100)

        Returns:
            dict: API response
        """
        return self.http.call(
            endpoint="entry.cgi",
            api="SYNO.Wifi.Radio.Setting",
            method="get",
            version=1,
            params={"radio_type": radio_type, "tx_power": tx_power},
        )

    def get_country_codes(self):
        """Get available country codes for WiFi regulation.

        Returns:
            dict: Available country codes with their restrictions
        """
        return self.http.call(
            endpoint="entry.cgi",
            api="SYNO.Wifi.CountryCode.Capability",
            method="get",
            version=1,
        )

    def get_current_country_code(self):
        """Get current country code setting.

        Returns:
            str: Current country code
        """
        response = self.http.call(
            endpoint="entry.cgi",
            api="SYNO.Wifi.CountryCode.Setting",
            method="get",
            version=1,
        )
        return response.get("country_code", "")

    def set_country_code(self, country_code):
        """Set country code for WiFi regulation.

        Args:
            country_code: Country code (e.g., 'UA', 'US', 'EU')

        Returns:
            dict: API response
        """
        return self.http.call(
            endpoint="entry.cgi",
            api="SYNO.Wifi.CountryCode.Setting",
            method="ge",
            version=1,
            params={"country_code": country_code},
        )

    def get_wps_status(self):
        """Get WPS (Wi-Fi Protected Setup) status.

        Returns:
            dict: WPS status information
        """
        response = self.http.call(
            endpoint="entry.cgi",
            api="SYNO.Wifi.WPS.Status",
            method="get",
            version=1,
        )

        return response.get("status_list", [])

    def start_wps_pbc(self):
        """Start WPS Push Button Configuration.

        Returns:
            dict: API response
        """
        return self.http.call(
            endpoint="entry.cgi",
            api="SYNO.Wifi.WPS.Main.PBC",
            method="start",
            version=1,
        )

    def stop_wps(self):
        """Stop WPS operation.

        Returns:
            dict: API response
        """
        return self.http.call(
            endpoint="entry.cgi",
            api="SYNO.Wifi.WPS.Main",
            method="stop",
            version=1,
        )

    def get_wps_pin(self):
        """Get WPS PIN code.

        Returns:
            str: WPS PIN code
        """
        response = self.http.call(
            endpoint="entry.cgi",
            api="SYNO.Wifi.WPS.Main.PIN.AP",
            method="get",
            version=1,
        )
        return response.get("pin", "")

    def start_wifi_scan(self, radio_type="2.4G"):
        """Start WiFi network scanning.

        Args:
            radio_type: Radio type to scan with (2.4G, 5G-1, 5G-2)

        Returns:
            dict: API response
        """
        return self.http.call(
            endpoint="entry.cgi",
            api="SYNO.Wifi.Station.Scan",
            method="start",
            version=1,
            params={"radio_type": radio_type},
        )

    def get_wifi_scan_results(self, radio_type="2.4G"):
        """Get WiFi scan results.

        Args:
            radio_type: Radio type that was scanned

        Returns:
            list: Scan results with found networks
        """
        response = self.http.call(
            endpoint="entry.cgi",
            api="SYNO.Wifi.Station.Scan",
            method="get",
            version=1,
            params={"radio_type": radio_type},
        )
        return response.get("networks", [])

    def get_mac_filter_profiles(self):
        """Get MAC filter profiles.

        Returns:
            list: List of MAC filter profiles
        """
        response = self.http.call(
            endpoint="entry.cgi",
            api="SYNO.Wifi.MACFilter.Profile",
            method="list",
            version=1,
        )
        return response.get("profiles", [])

    def create_mac_filter_profile(self, name, description=""):
        """Create new MAC filter profile.

        Args:
            name: Profile name
            description: Profile description

        Returns:
            dict: API response with new profile ID
        """
        return self.http.call(
            endpoint="entry.cgi",
            api="SYNO.Wifi.MACFilter.Profile",
            method="create",
            version=1,
            params={"name": name, "description": description},
        )

    def get_global_capability(self):
        """Get global WiFi capabilities.

        Returns:
            dict: Global WiFi capabilities
        """
        return self.http.call(
            endpoint="entry.cgi",
            api="SYNO.Wifi.Global.Capability",
            method="get",
            version=1,
        )

    def get_hw_button_status(self):
        """Get hardware WiFi button status.

        Returns:
            dict: Hardware button status
        """
        return self.http.call(
            endpoint="entry.cgi",
            api="SYNO.Wifi.Global.HWButton",
            method="get",
            version=1,
        )

    def set_hw_button_enabled(self, enabled):
        """Enable or disable hardware WiFi button.

        Args:
            enabled: True to enable, False to disable

        Returns:
            dict: API response
        """
        return self.http.call(
            endpoint="entry.cgi",
            api="SYNO.Wifi.Global.HWButton",
            method="set",
            version=1,
            params={"enabled": enabled},
        )

    def get_station_status(self):
        """Get WiFi station (client) status.

        Returns:
            dict: Station status when router is acting as WiFi client
        """
        return self.http.call(
            endpoint="entry.cgi",
            api="SYNO.Wifi.Station.Status",
            method="get",
            version=1,
        )

    def connect_to_network(
        self, ssid, password, security="wpa2_psk", radio_type="2.4G"
    ):
        """Connect to WiFi network as client.

        Args:
            ssid: Network SSID to connect to
            password: Network password
            security: Security type (open, wep, wpa_psk, wpa2_psk, etc.)
            radio_type: Radio type to use

        Returns:
            dict: API response
        """
        return self.http.call(
            endpoint="entry.cgi",
            api="SYNO.Wifi.Station.Setting",
            method="connect",
            version=1,
            params={
                "ssid": ssid,
                "password": password,
                "security": security,
                "radio_type": radio_type,
            },
        )

    def disconnect_from_network(self, radio_type="2.4G"):
        """Disconnect from WiFi network.

        Args:
            radio_type: Radio type to disconnect

        Returns:
            dict: API response
        """
        return self.http.call(
            endpoint="entry.cgi",
            api="SYNO.Wifi.Station.Setting",
            method="disconnect",
            version=1,
            params={"radio_type": radio_type},
        )
