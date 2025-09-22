# Quick Installation Guide - v1.0.1

## 🚀 Installing Worcester Bosch Wave Integration v1.0.1

### ✅ **HACS Installation (Recommended)**

1. **Open HACS** in Home Assistant
2. **Go to Integrations**
3. **Click the three dots menu (⋮)** → **Custom repositories**
4. **Add Repository**:
   - **URL**: `https://github.com/sadontsev/hass-worcester-bosch-wave-thermostat`
   - **Category**: Integration
   - **Click "Add"**
5. **Install Integration**:
   - Search for "Worcester Bosch Wave"
   - Click "Download" 
   - Restart Home Assistant
6. **Configure Integration**:
   - Settings → Devices & Services → Add Integration
   - Search "Worcester Bosch Wave"
   - Enter your credentials

### 🔧 **Manual Installation**

```bash
# SSH into Home Assistant or use Terminal add-on
cd /config/custom_components
git clone https://github.com/sadontsev/hass-worcester-bosch-wave-thermostat.git worcester_bosch_wave
# Restart Home Assistant, then add integration via UI
```

### 📋 **Required Credentials**

You'll need these from your Worcester Bosch Wave setup:

1. **Serial Number**: Found on thermostat hardware or in Wave app
2. **Access Code**: 4-digit code from thermostat (Menu → Settings → System → Access Code)
3. **Password**: Set when you configured the Wave mobile app

### 🎯 **What You'll Get**

After installation and configuration:
- **1 Climate Entity**: `climate.worcester_bosch_wave_thermostat`
- **19 Sensor Entities**: Individual temperature, control, and diagnostic sensors
- **9 Binary Sensor Entities**: Boolean status indicators
- **30+ Metrics**: Complete access via climate entity attributes

### 🔄 **Upgrading from v1.0.0**

If you had HACS installation issues with v1.0.0:
1. Remove the old repository from HACS custom repositories
2. Add the repository again (same URL)
3. Install v1.0.1
4. Your existing configuration will be preserved

### 🆘 **Troubleshooting**

#### HACS Issues
- Ensure repository URL is exactly: `https://github.com/sadontsev/hass-worcester-bosch-wave-thermostat`
- Category must be "Integration"
- If still having issues, try removing and re-adding the repository

#### Connection Issues
- Verify thermostat is online in Wave app
- Check Home Assistant can reach your network (VM users: check bridge config)
- Ensure credentials are correct (access code is case-sensitive)

#### Missing Entities
- Some metrics may not be available on all thermostat models
- Check Home Assistant logs for any errors
- Restart Home Assistant after installation

### ✅ **Quick Test**

After installation, check:
1. Climate entity appears in Home Assistant
2. Current temperature shows correctly
3. You can change target temperature
4. Sensor entities are populated with data

### 📖 **Documentation**

- **Full README**: [Repository Documentation](https://github.com/sadontsev/hass-worcester-bosch-wave-thermostat)
- **Troubleshooting**: Check repository issues for common problems
- **Community**: Home Assistant Community forum for general questions

---

**Ready to install?** v1.0.1 fixes all HACS compliance issues and provides comprehensive Worcester Bosch Wave integration! 🎉