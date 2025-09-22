# Worcester Bosch Wave Integration v1.0.1 🎉

## 🔧 HACS Compliance Release

This release fixes HACS repository structure compliance issues and ensures smooth installation.

### 🛠️ Bug Fixes & Improvements

- **✅ HACS Compliance**: Fixed repository structure issues that prevented HACS installation
- **✅ Repository URLs**: Updated all references to point to correct repository (`sadontsev/hass-worcester-bosch-wave-thermostat`)
- **✅ Configuration**: Fixed `hacs.json` content structure setting
- **✅ Ownership**: Updated codeowners and maintainer information

### 🌟 Features (from v1.0.0)

Complete Home Assistant integration for Worcester Bosch Wave thermostats with comprehensive metric support.

- **🌡️ Full Climate Control**: Set temperature, change modes (Heat/Auto/Off), real-time monitoring
- **📊 30+ Comprehensive Metrics**: Access to all available thermostat data
- **🏠 29 Total Entities**: 1 climate + 19 sensors + 9 binary sensors
- **🔧 HACS Compatible**: Easy installation through Home Assistant Community Store
- **🖥️ VM-Friendly**: Optimized for Home Assistant VM installations
- **⚡ Real-time Updates**: 30-second refresh interval with efficient coordinator pattern

### 🏠 Available Entities

#### Climate Entity (1)
- **Worcester Bosch Wave Thermostat**: Main control with all metrics as attributes

#### Sensor Entities (19)
- **Temperature Sensors (5)**: Current, Target, Manual, Switch Point, Schedule
- **Control Sensors (4)**: Program Mode, Control Mode, Boiler Status, System Health
- **Time Sensors (3)**: Override Duration, System Time, Time Remaining
- **Diagnostic Sensors (7)**: Schedule Point, Program Status, Reset Status, and more

#### Binary Sensor Entities (9)
- **Boiler Status**: Active, Enabled, Backup Enabled, Maintenance Required
- **System Features**: Holiday Mode, First Aid Help, Override Active
- **Hot Water**: Demand status

### 📋 Supported Metrics

#### Essential Metrics (4)
- **IHT** - Current Temperature
- **TSP** - Target Temperature  
- **BAI** - Boiler Status
- **UMD** - Program Mode

#### System Control (6)
- **CPM** - Control Mode
- **MMT** - Manual Temperature
- **CSP** - Current Switch Point
- **DHW** - Hot Water Demand
- **TOD** - Override Duration
- **TOT** - Schedule Temperature

#### Diagnostic & Advanced (20+)
- System Health, Boiler Control, Schedule Management
- Holiday Mode, Frost Protection, Energy Saving
- Timestamps, Program Timers, Reset Status
- And much more!

### 🚀 Installation

#### Via HACS (Recommended) - Now Working!
1. **Add Custom Repository**:
   - HACS → Integrations → ⋮ → Custom repositories
   - Repository: `https://github.com/sadontsev/hass-worcester-bosch-wave-thermostat`
   - Category: Integration

2. **Install**:
   - Search for "Worcester Bosch Wave"
   - Click Install
   - Restart Home Assistant

3. **Configure**:
   - Settings → Devices & Services → Add Integration
   - Search "Worcester Bosch Wave"
   - Enter thermostat credentials

#### Manual Installation
```bash
cd /config/custom_components
git clone https://github.com/sadontsev/hass-worcester-bosch-wave-thermostat.git worcester_bosch_wave
```

### 📋 Requirements

- **Home Assistant**: 2023.1.0 or higher
- **Worcester Bosch Wave thermostat** with app connectivity
- **Network access** to thermostat (same network or routable)
- **Credentials**: Serial number, access code (4-digit), and password

### 🔧 Configuration

You'll need three pieces of information from your Worcester Bosch Wave setup:

1. **Serial Number**: Found on thermostat hardware or in Wave app
2. **Access Code**: 4-digit code from thermostat display (Menu → Settings → System)
3. **Password**: Set when configuring the Wave mobile app

### 🎯 Usage Examples

#### Basic Automation
```yaml
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
```

#### Monitor Metrics
```yaml
# Access individual sensors
sensor.worcester_wave_current_temperature
sensor.worcester_wave_boiler_status
binary_sensor.worcester_wave_boiler_active

# Or use comprehensive attributes
{{ state_attr('climate.worcester_bosch_wave_thermostat', 'boiler_status') }}
```

### 🐛 Known Issues

- None at this time

### 🔄 Changelog

**v1.0.1** (Current)
- Fixed HACS repository structure compliance
- Updated repository URLs and ownership
- Corrected hacs.json configuration

**v1.0.0** 
- Initial release with complete functionality

### 🤝 Contributing

Issues and pull requests welcome at: https://github.com/sadontsev/hass-worcester-bosch-wave-thermostat

### 📝 Migration from v1.0.0

If you installed v1.0.0 and encountered HACS issues:
1. Remove the integration from HACS
2. Add the repository again
3. Install v1.0.1
4. No configuration changes needed

---

**Note**: This is an unofficial integration. Worcester Bosch and Wave are trademarks of their respective owners.