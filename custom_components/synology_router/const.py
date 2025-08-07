"""Constants for the Synology SRM integration."""

DOMAIN = "synology_router"

# Default configuration values
DEFAULT_PORT = 8000
DEFAULT_HOST = "192.168.0.1"
DEFAULT_SCAN_INTERVAL = 3

# Configuration keys
CONF_HTTPS = "https"

# Services
SERVICE_ENABLE_WIFI = "enable_wifi"
SERVICE_DISABLE_WIFI = "disable_wifi"
SERVICE_TOGGLE_SMART_CONNECT = "toggle_smart_connect"

# Service data keys
ATTR_PROFILE_ID = "profile_id"
ATTR_RADIO_TYPE = "radio_type"
ATTR_NETWORK_NAME = "network_name"
ATTR_ENABLE = "enable"

# Network types
NETWORK_TYPE_PRIMARY = "primary"
NETWORK_TYPE_GUEST = "guest"
NETWORK_TYPE_CUSTOM = "custom"

# Radio types
RADIO_TYPE_2_4G = "2.4G"
RADIO_TYPE_5G_1 = "5G-1"
RADIO_TYPE_5G_2 = "5G-2"
RADIO_TYPE_SMART_CONNECT = "SmartConnect"

# Switch types
SWITCH_TYPE_RADIO = "radio"
SWITCH_TYPE_SMART_CONNECT_TOGGLE = "smart_connect_toggle"

# Security levels
SECURITY_OPEN = "open"
SECURITY_WPA2_PSK = "wpa2_psk"
SECURITY_WPA3_PSK = "wpa3_psk"
SECURITY_WPA2_WPA3_PSK = "wpa2_wpa3_psk"
