# Synology SRM for Home Assistant

[![GitHub Latest Release](https://img.shields.io/github/release/Bryzgalin/synology-srm-ha.svg)](https://github.com/Bryzgalin/synology-srm-ha/releases)
[![GitHub All Releases](https://img.shields.io/github/downloads/Bryzgalin/synology-srm-ha/total.svg)](https://github.com/Bryzgalin/synology-srm-ha/releases)

A custom Home Assistant integration for Synology SRM (Synology Router Manager) that allows you to control your Synology router's WiFi networks directly from Home Assistant.

This integration uses a custom-modified version of the [synology-srm](https://github.com/aerialls/synology-srm) library, enhanced specifically for Home Assistant compatibility and additional WiFi management features.

## Features

- **WiFi Network Control**: Enable/disable individual WiFi networks (2.4G, 5G-1, 5G-2, SmartConnect)
- **Smart Connect Management**: Toggle Smart Connect mode for each network profile
- **Multiple Network Profiles**: Support for Primary, Guest, and custom network profiles  
- **Automatic Discovery**: Automatically discovers all configured WiFi networks
- **Real-time Status**: Live status updates of your WiFi networks
- **Services**: Control WiFi networks through Home Assistant services for automation

## Credits

This integration uses a modified version of the [synology-srm](https://github.com/aerialls/synology-srm) Python library by [@aerialls](https://github.com/aerialls), adapted and enhanced for Home Assistant integration with additional WiFi management capabilities.

## Supported Devices

This integration works with Synology routers running SRM (Synology Router Manager). 

**Tested on:**
- RT6600ax

**Should work with other RT/MR/WRX series routers, but not tested:**
- RT series (RT2600ac, RT1900ac, etc.)
- MR series (MR2200ac, etc.)
- WRX series (WRX560, etc.)

## Installation

### Manual Installation

1. Download the latest release from the [releases page](https://github.com/Bryzgalin/synology-srm-ha/releases)
2. Extract the files to your `custom_components` directory:
   ```
   custom_components/
   └── synology_srm/
       ├── __init__.py
       ├── manifest.json
       ├── config_flow.py
       └── ...
   ```
3. Restart Home Assistant

## Configuration

1. Go to **Settings** > **Devices & Services**
2. Click **Add Integration**
3. Search for "Synology SRM"
4. Enter your router details:
   - **Host**: IP address of your Synology router (e.g., `192.168.1.1`)
   - **Port**: API port (default: `8001`)
   - **Username**: Router admin username
   - **Password**: Router admin password
   - **Scan Interval**: Update frequency in seconds (default: `30`)

## Usage

### Switches

After setup, you'll see switches for each WiFi network:

- **Profile Name SmartConnect Toggle** - Controls Smart Connect mode
- **Profile Name - SSID (Radio Type)** - Controls individual radio networks

Example switches:
- `switch.primary_network_smartconnect_toggle`
- `switch.primary_network_homewifi_2_4g`
- `switch.guest_network_guestwifi_smartconnect`

### Smart Connect Logic

- When **Smart Connect is ON**: Only SmartConnect radios are available for control
- When **Smart Connect is OFF**: Individual radios (2.4G, 5G-1, 5G-2) are available for control

### Services

The integration provides services for automation:

#### `synology_srm.enable_wifi`
Enable a WiFi network by profile ID and radio type, or by network name.

```yaml
service: synology_srm.enable_wifi
data:
  profile_id: 1
  radio_type: "2.4G"
# OR
service: synology_srm.enable_wifi
data:
  network_name: "GuestWiFi"
```

#### `synology_srm.disable_wifi`
Disable a WiFi network by profile ID and radio type, or by network name.

```yaml
service: synology_srm.disable_wifi
data:
  profile_id: 0
  radio_type: "5G-1"
```

#### `synology_srm.toggle_smart_connect`
Toggle Smart Connect mode for a profile.

```yaml
service: synology_srm.toggle_smart_connect
data:
  profile_id: 0
  enable: true
```

## Automation Examples

### Schedule Guest WiFi
```yaml
automation:
  - alias: "Enable Guest WiFi during day"
    trigger:
      - platform: time
        at: "08:00:00"
    action:
      - service: synology_srm.enable_wifi
        data:
          network_name: "GuestWiFi"
  
  - alias: "Disable Guest WiFi at night"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: synology_srm.disable_wifi
        data:
          network_name: "GuestWiFi"
```

### Smart Connect Control
```yaml
automation:
  - alias: "Switch to individual radios for better control"
    trigger:
      - platform: state
        entity_id: input_boolean.advanced_wifi_mode
        to: 'on'
    action:
      - service: synology_srm.toggle_smart_connect
        data:
          profile_id: 0
          enable: false
```

## Troubleshooting

### Connection Issues
- Verify router IP address and port
- Check username/password credentials
- Ensure router is accessible from Home Assistant
- Try disabling HTTPS if using custom port

### Missing Networks
- Networks may not appear if they're disabled on the router
- Check router configuration for all network profiles
- Restart the integration after router configuration changes

### Entity Unavailable
- Check network connectivity to router
- Verify router API is responding
- Look at Home Assistant logs for detailed error messages

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.

## Changelog

### v1.0.0
- Initial release
- WiFi network control switches
- Smart Connect toggle functionality
- Services for automation
- Support for multiple network profiles
