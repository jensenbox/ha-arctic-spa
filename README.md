# Arctic Spa – Home Assistant Integration

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/closient/ha-arctic-spa)](https://github.com/closient/ha-arctic-spa/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Home Assistant custom integration for [Arctic Spas](https://www.arcticspas.com/) hot tubs using the official cloud API. Provides real-time monitoring, temperature control, pump/light switching, SpaBoy water chemistry tracking, and filtration management — all as a single HA device.

## Features

- **Temperature monitoring & control** — current water temp, setpoint adjustment via slider
- **Pump control** — toggle jets on/off for Pump 1 (3-speed) and Pump 2
- **Light control** — switch spa lights on/off
- **SpaBoy water chemistry** — real-time pH and ORP readings with status indicators
- **Filtration management** — adjust duration and frequency
- **Boost mode** — quick-heat toggle
- **Error reporting** — surface spa errors as HA sensors
- **Connectivity monitoring** — know when your spa goes offline
- **Single device** — all entities grouped under one device, assignable to an area

## Prerequisites

You need an Arctic Spa API key. Log into your account at [myarcticspa.com](https://myarcticspa.com) and visit the [API Key Management](https://myarcticspa.com/spa/SpaAPIManagement.aspx) page to generate one. If the page isn't available, contact Arctic Spas support to request API access.

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the three dots menu (⋮) → **Custom repositories**
3. Add `https://github.com/closient/ha-arctic-spa` with category **Integration**
4. Search for "Arctic Spa" in HACS and click **Install**
5. Restart Home Assistant

### Manual

1. Copy the `custom_components/arctic_spa` directory to your Home Assistant `custom_components` folder:

```
custom_components/
  arctic_spa/
    __init__.py
    api.py
    binary_sensor.py
    config_flow.py
    const.py
    coordinator.py
    entity.py
    manifest.json
    number.py
    sensor.py
    strings.json
    switch.py
    translations/
      en.json
```

2. Restart Home Assistant

## Setup

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **Arctic Spa**
3. Enter your API key
4. Your spa will appear as a device with all entities

## Entities

### Sensors

| Entity | Description | Unit |
|--------|-------------|------|
| Temperature | Current water temperature | °F |
| Setpoint | Target temperature | °F |
| pH | SpaBoy pH reading | pH |
| pH Status | SpaBoy pH status (OK, Caution High, etc.) | — |
| ORP | SpaBoy oxidation-reduction potential | mV |
| ORP Status | SpaBoy ORP status | — |
| Filter Status | Current filter state (Idle, Filtering, Overtemperature) | — |
| Filtration Duration | Configured filter cycle length | hr |
| Filtration Frequency | Configured cycles per day | x/day |
| Pump 1 State | Pump 1 state (off, low, high) | — |
| Pump 2 State | Pump 2 state (off, high) | — |
| Errors | Active error codes or "None" | — |

### Binary Sensors

| Entity | Description | Device Class |
|--------|-------------|--------------|
| Connected | Spa cloud connectivity | connectivity |
| SpaBoy Connected | SpaBoy module connectivity | connectivity |
| SpaBoy Producing | SpaBoy actively producing sanitizer | — |
| Lights | Light state (for automation triggers) | light |
| Filter Suspension | Overtemp filter suspension active | — |
| Pump 1 Running | Pump 1 is running (any speed) | running |
| Pump 2 Running | Pump 2 is running | running |
| Has Errors | Spa is reporting errors | problem |

### Switches

| Entity | Description |
|--------|-------------|
| Lights | Toggle spa lights on/off |
| Pump 1 Jets | Toggle Pump 1 (high speed) |
| Pump 2 Jets | Toggle Pump 2 |
| Boost Mode | Quick-heat boost |

### Numbers (Controls)

| Entity | Range | Description |
|--------|-------|-------------|
| Temperature Setpoint | 80–104 °F | Adjust target water temperature |
| Filtration Duration | 1–24 hr | Filter cycle length |
| Filtration Frequency | 1–24 x/day | Filter cycles per day |

## Automation Examples

### Alert when pH is out of range

```yaml
automation:
  - alias: "Spa pH Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.arctic_spa_ph
        above: 7.6
        for: { hours: 1 }
      - platform: numeric_state
        entity_id: sensor.arctic_spa_ph
        below: 7.2
        for: { hours: 1 }
    action:
      - action: notify.mobile_app_your_phone
        data:
          title: "🧪 Spa pH Alert"
          message: "pH is {{ states('sensor.arctic_spa_ph') }} (target: 7.2–7.6)"
```

### Alert when spa goes offline

```yaml
automation:
  - alias: "Spa Offline Alert"
    trigger:
      - platform: state
        entity_id: binary_sensor.arctic_spa_connected
        to: "off"
        for: { minutes: 10 }
    action:
      - action: notify.mobile_app_your_phone
        data:
          title: "🔌 Spa Offline"
          message: "Arctic Spa has been disconnected for 10 minutes"
```

### Pre-heat before evening soak

```yaml
automation:
  - alias: "Pre-heat Spa"
    trigger:
      - platform: time
        at: "17:00:00"
    condition:
      - condition: time
        weekday: [fri, sat, sun]
    action:
      - action: number.set_value
        target:
          entity_id: number.arctic_spa_temperature_setpoint
        data:
          value: 104
```

## API

This integration uses the [Arctic Spa Cloud API](https://api.myarcticspa.com/docs). The API provides:

- `GET /v2/spa/status` — read spa state (polled every 60 seconds)
- `PUT /v2/spa/lights` — control lights
- `PUT /v2/spa/pumps/{id}` — control pumps
- `PUT /v2/spa/temperature` — set target temperature
- `PUT /v2/spa/filter` — configure filtration
- `PUT /v2/spa/boost` — toggle boost mode

## Tested Models

- **McKinley** (449 gal, 2-pump, SpaBoy)

If you have a different Arctic Spa model, please [open an issue](https://github.com/closient/ha-arctic-spa/issues) to report compatibility.

## Contributing

Contributions are welcome! Please open an issue first to discuss what you'd like to change.

## License

[MIT](LICENSE)
