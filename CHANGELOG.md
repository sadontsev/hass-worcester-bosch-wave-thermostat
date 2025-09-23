# Changelog

All notable changes to the Worcester Bosch Wave Home Assistant integration will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.8] - 2025-09-23

### Added

### Notes

## [1.0.9] - 2025-09-24
- Fix blocking SSL cert load by moving XMPP client construction to executor in config flow
- Refactor async client to construct WaveStatus/WaveSet inside executors to avoid event loop blocking
- Fix slixmpp connect() compatibility (use positional address tuple)
- Minor coordinator init cleanup

## [1.0.10] - 2025-09-24
- Fix "There is no current event loop in thread 'SyncWorker_*'" by creating a thread-local asyncio loop in executor tasks before constructing slixmpp clients

## [1.0.6] - 2025-09-22

### Fixed
- Corrected a regression in XMPP messenger initialization (indentation) and explicitly disabled TLS/SSL in connect() parameters.

## [1.0.5] - 2025-09-22

### Fixed
- Stabilized XMPP connection logic in `worcester_bosch_wave/messenger.py` to properly process events with a timeout and disconnect cleanly.
- Improved config flow error handling to distinguish invalid credentials vs connection failure.

### Notes
- If you previously saw "Failed to connect" when adding the device, please upgrade to v1.0.5 and try again.

## [1.0.4] - 2025-09-22

### Fixed
- Corrected HACS release configuration: previous tag v1.0.3 contained `zip_release: true` and `persistent_directory` in hacs.json, which caused HACS install errors. These are now fixed; `zip_release` is `false` and invalid fields removed going forward.

### Notes
- Please install v1.0.4 or later via HACS. If you installed v1.0.3 and saw "Unknown error", upgrade to 1.0.4.

## [1.0.3] - 2025-09-22

### Fixed
- **Critical**: Removed duplicate `async_unload_entry` function in `__init__.py`
- **Critical**: Fixed coordinator shutdown handling in integration unload
- **Enhancement**: Added proper async client wrapper for Worcester Bosch Wave library
- **Enhancement**: Added English translations for config flow (improved UX)
- **Quality**: Fixed all syntax errors and code quality issues

### Added
- `translations/en.json`: Proper localization support for config flow
- `worcester_bosch_wave/wave_client.py`: Async wrapper for thermostat communication
- Complete integration lifecycle testing (load/unload/reload)

### Changed
- Integration now properly handles shutdown and cleanup
- Improved error handling in config flow with proper translations
- Enhanced reliability for HACS installation and management

### Technical
- 100% Python syntax validation passed
- All JSON schemas validated
- HACS compliance verified
- Integration lifecycle tested

## [1.0.1] - 2025-09-22

### Fixed
- HACS repository structure compliance issues
- Repository URLs in manifest.json now point to correct repository (sadontsev)
- hacs.json configuration corrected with `content_in_root: true`
- Updated codeowners to @sadontsev

### Changed
- Integration now installs correctly via HACS without compliance errors

## [1.0.0] - 2025-09-22

### Added
- Initial release of Worcester Bosch Wave Home Assistant integration
- Complete climate entity with full thermostat control
- 19 individual sensor entities for comprehensive monitoring
- 9 binary sensor entities for boolean status indicators
- Support for 30+ thermostat metrics organized in logical categories
- HACS compatibility for easy installation
- Data update coordinator for efficient API management
- User-friendly config flow for credential setup

### Features
- **Climate Control**: Temperature setting, HVAC mode control (Heat/Auto/Off)
- **Real-time Monitoring**: Current temperature, target temperature, heating status
- **Comprehensive Metrics**: All available thermostat data accessible
- **Multiple Access Methods**: Individual sensors OR comprehensive attributes on climate entity
- **VM-Friendly**: Optimized for Home Assistant VM installations
- **Efficient Updates**: 30-second refresh interval with smart coordinator pattern

### Supported Metrics
#### Essential (4)
- Current Temperature (IHT)
- Target Temperature (TSP)
- Boiler Status (BAI)
- Program Mode (UMD)

#### System Control (6)
- Control Mode (CPM)
- Manual Temperature (MMT)
- Current Switch Point (CSP)
- Hot Water Demand (DHW)
- Override Duration (TOD)
- Schedule Temperature (TOT)

#### Diagnostic & Advanced (20+)
- System Health (IHS)
- Program Running (PMR)
- Boiler Control (BLE, BBE, BMR)
- Schedule Management (ARS, CTD, CTR)
- System Features (Holiday Mode, Frost Protection, Energy Saving)
- And more diagnostic data

### Technical Details
- Requires Home Assistant 2023.1+
- Uses slixmpp for XMPP communication
- Implements coordinator pattern for data management
- Supports config flow for easy setup
- Compatible with Worcester Bosch Wave thermostats with app connectivity

---

## Release Notes

### v1.0.1 - HACS Compliance Fix
This release resolves HACS installation issues. If you experienced problems installing v1.0.0 via HACS, v1.0.1 should install without issues.

### v1.0.0 - Initial Release
Complete Home Assistant integration providing comprehensive access to Worcester Bosch Wave thermostat functionality and data.
