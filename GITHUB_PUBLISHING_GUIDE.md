# GitHub Publishing Guide for Worcester Bosch Wave Integration

This guide will help you publish your Worcester Bosch Wave Home Assistant integration to GitHub and make it available through HACS for easy installation on VM-based Home Assistant systems.

## 📋 Pre-Publishing Checklist

### ✅ Files Ready for Publishing
- [x] `manifest.json` - HACS-compatible with proper domain
- [x] `__init__.py` - Integration entry point with coordinator
- [x] `config_flow.py` - User-friendly setup flow
- [x] `const.py` - Integration constants
- [x] `coordinator.py` - Data update coordinator
- [x] `climate.py` - Main climate entity with all 30 metrics
- [x] `sensor.py` - Individual sensor entities (temperature, control, diagnostic)
- [x] `binary_sensor.py` - Binary sensor entities (boolean indicators)
- [x] `hacs.json` - HACS configuration
- [x] `README_HACS.md` - Comprehensive user documentation
- [x] All Worcester Bosch Wave library files in `worcester_bosch_wave/`

## 🚀 Step 1: Create GitHub Repository

### 1.1 Create New Repository
```bash
# Navigate to your project directory
cd /Users/max/ai-projects/hass-worcester-bosch-wave-thermostat

# Initialize git repository (if not already done)
git init

# Create .gitignore
cat > .gitignore << EOF
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/
.pytest_cache/
.coverage
.mypy_cache/
.DS_Store
EOF
```

### 1.2 Add Files to Repository
```bash
# Add all integration files
git add .
git commit -m "Initial commit: Worcester Bosch Wave HA integration with 30+ metrics"

# Create GitHub repository (replace USERNAME with your GitHub username)
# Go to https://github.com/new and create repository:
# Name: hass-worcester-bosch-wave-thermostat
# Description: Home Assistant integration for Worcester Bosch Wave thermostats
# Public repository (for HACS compatibility)
# Don't initialize with README (we have our own)

# Add remote and push
git remote add origin https://github.com/USERNAME/hass-worcester-bosch-wave-thermostat.git
git branch -M main
git push -u origin main
```

## 📝 Step 2: Repository Setup

### 2.1 Update Repository Settings
1. **About Section**:
   - Description: "Comprehensive Home Assistant integration for Worcester Bosch Wave thermostats"
   - Website: Your Home Assistant instance URL (optional)
   - Topics: `home-assistant`, `hacs`, `worcester-bosch`, `wave`, `thermostat`, `climate`, `smart-home`

2. **Releases**:
   - Go to "Releases" → "Create a new release"
   - Tag: `v1.0.0`
   - Title: `Worcester Bosch Wave Integration v1.0.0`
   - Description: See release notes below

### 2.2 Release Notes Template
```markdown
# # Worcester Bosch Wave Integration v1.0.1

## 🔧 HACS Compliance Release

This release fixes HACS repository structure compliance issues and ensures smooth installation.

### 🛠️ Bug Fixes & Improvements
- **HACS Compliance**: Fixed repository structure issues that prevented HACS installation
- **Repository URLs**: Updated all references to point to correct repository
- **Configuration**: Fixed hacs.json content structure setting  
- **Ownership**: Updated codeowners and maintainer information

### ✨ Features (Complete Integration)
- **Complete Climate Control**: Set temperature, change modes (Heat/Auto/Off)
- **30+ Metrics**: Access to all available thermostat data
- **Multiple Platforms**: Climate, Sensor, and Binary Sensor entities
- **HACS Compatible**: Easy installation through HACS (now working!)
- **VM-Friendly**: Optimized for Home Assistant VM installations

### 🏠 Available Entities
- **1 Climate Entity**: Main thermostat control with all metrics as attributes
- **19 Sensor Entities**: Temperature, control, time, and diagnostic sensors  
- **9 Binary Sensor Entities**: Boolean status indicators

### 📊 Supported Metrics
#### Essential (4)
- Current Temperature (IHT), Target Temperature (TSP), Boiler Status (BAI), Program Mode (UMD)

#### System Control (6)
- Control Mode (CPM), Manual Temperature (MMT), Switch Point (CSP), Hot Water (DHW), Override Duration (TOD), Schedule Temperature (TOT)

#### Diagnostic (20+)
- System Health, Boiler Control, Schedule Management, Holiday Mode, Frost Protection, Energy Saving, and more

### 🔧 Installation
1. Install via HACS (recommended) - now working correctly!
2. Add integration through Home Assistant UI
3. Enter thermostat credentials (Serial, Access Code, Password)

### 📋 Requirements
- Home Assistant 2023.1+
- Worcester Bosch Wave thermostat with app connectivity
- Network access to thermostat

### 🐛 Fixed Issues
- HACS repository structure compliance
- Incorrect repository URLs in manifest.json
- Content structure configuration in hacs.json

### 🔄 Changelog
**v1.0.1** - HACS compliance fixes and repository corrections
**v1.0.0** - Initial release with complete functionality

### 📝 Migration Notes
If you had issues with v1.0.0, simply update to v1.0.1 through HACS or reinstall.
```

## 🔧 Step 3: HACS Preparation

### 3.1 Update URLs in Files
Replace placeholder URLs in these files:
- `README_HACS.md`: Update GitHub repository URLs
- `manifest.json`: Update issue tracker URL if desired

### 3.2 File Structure Verification
Ensure your repository has this structure:
```
├── README.md (keep existing development docs)
├── README_HACS.md (HACS user documentation)
├── LICENSE
├── hacs.json
├── manifest.json
├── const.py
├── __init__.py
├── config_flow.py
├── coordinator.py
├── climate.py
├── sensor.py
├── binary_sensor.py
├── requirements.txt
├── pyproject.toml
├── worcester_bosch_wave/
│   ├── __init__.py
│   ├── wave_thermo.py
│   ├── status.py
│   ├── set.py
│   ├── messenger.py
│   ├── utils.py
│   ├── constants.py
│   └── example.py
└── (other existing files)
```

## 📦 Step 4: HACS Integration

### 4.1 Add to HACS (For Users)
Users will add your repository to HACS:
1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click three dots menu → "Custom repositories"
4. Add URL: `https://github.com/USERNAME/hass-worcester-bosch-wave-thermostat`
5. Category: "Integration"
6. Click "Add"

### 4.2 Official HACS Submission (Optional)
For inclusion in the default HACS store:
1. Repository must be public with good documentation
2. Submit to: https://github.com/hacs/default
3. Follow their submission guidelines
4. Wait for review and approval

## 🎯 Step 5: VM-Specific Installation Guide

### 5.1 VM Network Configuration
For Home Assistant VM users, add this section to documentation:

```markdown
## VM-Specific Setup

### Network Requirements
- Ensure VM has access to your home network
- Thermostat must be on same network or routable network
- Allow outbound connections on port 5222 (XMPP)

### Installation Steps
1. **HACS Installation** (easiest):
   - Add custom repository in HACS
   - Install integration
   - Restart Home Assistant

2. **Manual Installation**:
   ```bash
   # SSH into Home Assistant VM or use Terminal add-on
   cd /config/custom_components
   git clone https://github.com/USERNAME/hass-worcester-bosch-wave-thermostat.git worcester_bosch_wave
   ```

3. **Configuration**:
   - Settings → Devices & Services → Add Integration
   - Search "Worcester Bosch Wave"
   - Enter credentials from Wave app

### Troubleshooting VM Issues
- **Connection timeouts**: Check VM network bridge configuration
- **DNS resolution**: Ensure VM can resolve external domains
- **Firewall**: Check if VM firewall blocks outbound XMPP connections
```

## 📚 Step 6: Documentation Updates

### 6.1 Update Repository README
Consider renaming files:
- Keep current `README.md` for development
- Use `README_HACS.md` as the main user-facing documentation
- Or merge both with clear sections

### 6.2 Add Development Section
Add to README:
```markdown
## Development

### Local Testing
See original development setup in this repository for local testing instructions.

### Contributing
1. Fork the repository
2. Create a feature branch
3. Test your changes locally
4. Submit a pull request

### Code Structure
- `worcester_bosch_wave/`: Core thermostat communication library
- `climate.py`: Main climate entity
- `sensor.py`: Individual sensor entities  
- `binary_sensor.py`: Binary sensor entities
- `coordinator.py`: Data update coordinator
```

## 🎉 Step 7: Announce and Share

### 7.1 Community Sharing
- Post on Home Assistant Community forum
- Share on Reddit r/homeassistant
- Consider Home Assistant Discord

### 7.2 Documentation Links
- Link to your GitHub repository
- Provide installation instructions
- Include screenshots if possible

## 🔄 Step 8: Maintenance

### 8.1 Version Management
- Use semantic versioning (v1.0.0, v1.1.0, etc.)
- Create releases for significant updates
- Update `manifest.json` version field

### 8.2 Issue Management
- Monitor GitHub issues
- Respond to user questions
- Keep documentation updated

---

## Quick Commands Summary

```bash
# Initial repository setup
git init
git add .
git commit -m "Initial commit: Worcester Bosch Wave HA integration"
git remote add origin https://github.com/USERNAME/hass-worcester-bosch-wave-thermostat.git
git push -u origin main

# Create release
git tag v1.0.0
git push origin v1.0.0

# Update for new version
git add .
git commit -m "Update: description of changes"
git tag v1.1.0
git push origin main
git push origin v1.1.0
```

Your integration is now ready for HACS distribution and easy installation on VM-based Home Assistant systems!