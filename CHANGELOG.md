# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Reauth flow: if your API key is revoked or changed, Home Assistant will prompt you to re-enter it rather than requiring a full remove/re-add
- `entity_category` assignments: diagnostic entities (connectivity, errors, filter status, chemistry status) are now grouped as diagnostic; config entities (filtration duration/frequency, boost mode) are grouped as config
- Developer setup instructions in README
- Known Limitations and Troubleshooting sections in README
- Arctic Spa API documentation links (interactive docs and OpenAPI spec)

### Fixed
- CI workflow now triggers on `master` branch (was incorrectly set to `main`, causing CI to never run)
- `sensor.py`: added `None` guard on `native_value` to prevent `AttributeError` when coordinator data is unavailable
- `config_flow.py`: removed duplicate `client.close()` call on success path
- `api.py` `_put`: now raises `ArcticSpaApiError`/`ArcticSpaConnectionError` on failure instead of silently returning `False`, making command errors visible and loggable
- `api.py` `async_set_pump`: added bounds validation for `pump_id` (must be 1 or 2)
- `number.py`: filtration duration/frequency setters now safely handle `None` coordinator data

### Changed
- Temperature sensors and number entities now use `UnitOfTemperature.FAHRENHEIT` constant (enables HA unit conversion system for metric users)
- Filtration Duration sensor now uses `UnitOfTime.HOURS` constant
- `SpaBoy Producing` binary sensor icon changed from `mdi:chemical-weapon` to `mdi:flask`
- Switch and number command handlers now log errors on API failure instead of silently ignoring them
- Migrated from legacy `hass.data[DOMAIN]` pattern to `entry.runtime_data` (HA 2024.x+ best practice)
- `coordinator.py`: auth errors during polling now raise `ConfigEntryAuthFailed` (triggers reauth flow) instead of `UpdateFailed`
- Coordinator now receives `config_entry` parameter per HA 2024.x+ pattern
- Config flow now uses HA-managed aiohttp session (`async_get_clientsession`) for consistency with runtime behaviour
- README: corrected "Pump 1 (3-speed)" to clarify switch controls high speed only

### Removed
- Redundant explicit device registration from `__init__.py` (device is auto-created by HA when entities register their `device_info`)
- `hacs.json`: removed invalid `domains` and `iot_class` fields

### Configuration
- `hacs.json`: added `"zip_release": true` to direct HACS to use the release zip artifact

## [1.0.0] - 2025-01-01

### Added
- Initial release
- Temperature monitoring and setpoint control
- Pump 1 and Pump 2 jet switching (on/off, high speed)
- Light switching
- SpaBoy water chemistry monitoring (pH, ORP, status)
- Filtration schedule management (duration and frequency)
- Boost mode switch
- Error reporting sensors
- Connectivity monitoring
- Home Assistant config flow setup
- HACS compatibility
