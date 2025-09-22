# Worcester Bosch Wave Thermostat - Home Assistant Integration

A comprehensive Home Assistant integration for Worcester Bosch Wave thermostats, providing complete climate control and access to all 30+ available thermostat metrics.

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub Release](https://img.shields.io/github/release/username/hass-worcester-bosch-wave-thermostat.svg)](https://github.com/username/hass-worcester-bosch-wave-thermostat/releases)
[![License](https://img.shields.io/github/license/username/hass-worcester-bosch-wave-thermostat.svg)](LICENSE)

## Features

### 🌡️ Complete Climate Control
- **Full thermostat control**: Set temperature, change modes (Heat/Auto/Off)
- **Real-time monitoring**: Current temperature, target temperature, heating status
- **Program management**: Manual override, automatic scheduling, holiday mode

### 📊 Comprehensive Sensor Data
This integration provides access to **30+ metrics** organized into logical categories:

#### Essential Metrics (4)
- **Current Temperature** (IHT) - Real-time room temperature
- **Target Temperature** (TSP) - Desired temperature setting
- **Boiler Status** (BAI) - Active heating indicator
- **Program Mode** (UMD) - Manual/Auto/Program mode

#### System Control (6) 
- **Control Mode** (CPM) - Current control algorithm
- **Manual Temperature** (MMT) - Manual override temperature
- **Current Switch Point** (CSP) - Active schedule point
- **Hot Water Demand** (DHW) - Hot water system status
- **Override Duration** (TOD) - Time remaining for manual override
- **Schedule Temperature** (TOT) - Programmed temperature

#### Diagnostic & Advanced (20+)
- **System Health** (IHS) - Overall system status
- **Boiler Control**: Enable/disable, backup boiler, maintenance alerts
- **Schedule Management**: Current program, time remaining, schedule points
- **System Features**: Holiday mode, frost protection, energy saving
- **Timestamps**: System time, update times, program timers

### 🏠 Home Assistant Platforms

1. **Climate Entity**: Main thermostat control with all metrics as attributes
2. **Individual Sensors**: Temperature, control, and time-based sensors
3. **Binary Sensors**: Boolean status indicators (boiler active, maintenance required, etc.)

## Installation

### HACS Installation (Recommended)

1. **Add Custom Repository**:
   - Open HACS in Home Assistant
   - Go to "Integrations"
   - Click the three dots menu → "Custom repositories"
   - Add this repository URL: `https://github.com/username/hass-worcester-bosch-wave-thermostat`
   - Category: "Integration"

2. **Install Integration**:
   - Search for "Worcester Bosch Wave"
   - Click "Download"
   - Restart Home Assistant

3. **Add Integration**:
   - Go to Settings → Devices & Services
   - Click "Add Integration"
   - Search for "Worcester Bosch Wave"
   - Follow the configuration steps

### Manual Installation

1. **Download Files**:
   ```bash
   cd /config/custom_components
   git clone https://github.com/username/hass-worcester-bosch-wave-thermostat.git worcester_bosch_wave
   ```

2. **Restart Home Assistant**

3. **Add Integration** via Settings → Devices & Services

## Configuration

### Required Information
You'll need these details from your Worcester Bosch Wave app:

- **Serial Number**: Your thermostat's unique identifier
- **Access Code**: 4-digit code from the thermostat display  
- **Password**: Password set in the Wave app

### Finding Your Credentials

1. **Serial Number**: 
   - Found on the thermostat hardware label
   - Also visible in the Wave mobile app

2. **Access Code**:
   - Display on thermostat: Menu → Settings → System → Access Code
   - 4-digit numeric code

3. **Password**:
   - Set when configuring the Wave app
   - Used for remote access

## Usage

### Basic Climate Control

```yaml
# Example automation to set temperature
automation:
  - alias: "Morning Heating"
    trigger:
      - platform: time
        at: "07:00:00"
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.worcester_bosch_wave_thermostat
        data:
          temperature: 21

# Set HVAC mode
  - service: climate.set_hvac_mode
    target:
      entity_id: climate.worcester_bosch_wave_thermostat
    data:
      hvac_mode: "auto"
```

### Accessing Individual Sensors

```yaml
# Monitor specific metrics
- sensor.worcester_wave_current_temperature
- sensor.worcester_wave_target_temperature  
- sensor.worcester_wave_boiler_status
- sensor.worcester_wave_program_mode
- binary_sensor.worcester_wave_boiler_active
- binary_sensor.worcester_wave_maintenance_required
```

### Using Comprehensive Attributes

All 30+ metrics are available as attributes on the main climate entity:

```yaml
# Template sensor using attributes
sensor:
  - platform: template
    sensors:
      heating_efficiency:
        friendly_name: "Heating Efficiency"
        value_template: >
          {% set attrs = state_attr('climate.worcester_bosch_wave_thermostat', 'energy_saving') %}
          {{ 'High' if attrs == 'on' else 'Standard' }}
```

## Advanced Configuration

### Multiple Implementation Levels

Choose your preferred level of integration:

1. **Basic**: Climate entity only (minimal sensors)
2. **Enhanced**: Climate + essential sensors (recommended)  
3. **Comprehensive**: All entities + individual sensors (advanced users)

Configure in integration options after setup.

### Customizing Update Frequency

Default update interval is 30 seconds. Modify in `coordinator.py`:

```python
UPDATE_INTERVAL = timedelta(seconds=60)  # Reduce API calls
```

## Troubleshooting

### Common Issues

1. **Connection Failed**:
   - Verify credentials are correct
   - Check thermostat is online in Wave app
   - Ensure Home Assistant can reach thermostat network

2. **Authentication Errors**:
   - Re-check 4-digit access code
   - Verify password matches Wave app
   - Try regenerating access code on thermostat

3. **Missing Sensors**:
   - Some metrics may not be available on all thermostat models
   - Check entity registry for disabled entities
   - Enable additional platforms in integration options

### Debug Logging

Enable detailed logging in `configuration.yaml`:

```yaml
logger:
  default: warning
  logs:
    custom_components.worcester_bosch_wave: debug
    custom_components.worcester_bosch_wave.worcester_bosch_wave: debug
```

### Network Configuration

For VM-based Home Assistant installations:

1. **Network Access**: Ensure VM can reach thermostat network
2. **Firewall**: Allow outbound XMPP connections (port 5222)
3. **DNS**: Verify domain resolution for Worcester Bosch servers

## Supported Models

- Worcester Bosch Wave thermostats with app connectivity
- Requires Wave app setup and internet connection
- Compatible with all Wave-enabled boiler models

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Worcester Bosch for the Wave thermostat platform
- Home Assistant community for integration patterns
- XMPP protocol implementation using slixmpp

## Support

- **Issues**: [GitHub Issues](https://github.com/username/hass-worcester-bosch-wave-thermostat/issues)
- **Discussions**: [GitHub Discussions](https://github.com/username/hass-worcester-bosch-wave-thermostat/discussions)
- **Home Assistant Community**: [Community Forum](https://community.home-assistant.io/)

---

**Note**: This is an unofficial integration. Worcester Bosch and Wave are trademarks of their respective owners.