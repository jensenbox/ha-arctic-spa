"""Sensor platform for Arctic Spa."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import ArcticSpaEntity

SENSORS = [
    # (key, name, json_key, unit, device_class, state_class, icon, value_fn)
    (
        "temperature",
        "Temperature",
        "temperatureF",
        "°F",
        SensorDeviceClass.TEMPERATURE,
        SensorStateClass.MEASUREMENT,
        None,
        None,
    ),
    (
        "setpoint",
        "Setpoint",
        "setpointF",
        "°F",
        SensorDeviceClass.TEMPERATURE,
        None,
        None,
        None,
    ),
    (
        "ph",
        "pH",
        "ph",
        "pH",
        None,
        SensorStateClass.MEASUREMENT,
        "mdi:test-tube",
        None,
    ),
    (
        "ph_status",
        "pH Status",
        "ph_status",
        None,
        None,
        None,
        "mdi:test-tube",
        lambda v: v.replace("_", " ").title() if isinstance(v, str) else v,
    ),
    (
        "orp",
        "ORP",
        "orp",
        "mV",
        None,
        SensorStateClass.MEASUREMENT,
        "mdi:flash",
        None,
    ),
    (
        "orp_status",
        "ORP Status",
        "orp_status",
        None,
        None,
        None,
        "mdi:flash",
        lambda v: v.replace("_", " ").title() if isinstance(v, str) else v,
    ),
    (
        "filter_status",
        "Filter Status",
        "filter_status",
        None,
        None,
        None,
        "mdi:air-filter",
        None,
    ),
    (
        "filtration_duration",
        "Filtration Duration",
        "filtration_duration",
        "hr",
        None,
        None,
        "mdi:timer-outline",
        None,
    ),
    (
        "filtration_frequency",
        "Filtration Frequency",
        "filtration_frequency",
        "x/day",
        None,
        None,
        "mdi:refresh",
        None,
    ),
    (
        "pump1_state",
        "Pump 1 State",
        "pump1",
        None,
        None,
        None,
        "mdi:pump",
        None,
    ),
    (
        "pump2_state",
        "Pump 2 State",
        "pump2",
        None,
        None,
        None,
        "mdi:pump",
        None,
    ),
    (
        "errors",
        "Errors",
        "errors",
        None,
        None,
        None,
        "mdi:alert-circle-outline",
        lambda v: ", ".join(v) if isinstance(v, list) and v else "None",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Arctic Spa sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for key, name, json_key, unit, dev_cls, state_cls, icon, value_fn in SENSORS:
        entities.append(
            ArcticSpaSensor(
                coordinator,
                entry.entry_id,
                key,
                name,
                json_key,
                unit,
                dev_cls,
                state_cls,
                icon,
                value_fn,
            )
        )
    async_add_entities(entities)


class ArcticSpaSensor(ArcticSpaEntity, SensorEntity):
    """Representation of an Arctic Spa sensor."""

    def __init__(
        self,
        coordinator,
        entry_id,
        key,
        name,
        json_key,
        unit,
        device_class,
        state_class,
        icon,
        value_fn,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator, entry_id, key, name)
        self._json_key = json_key
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_icon = icon
        self._value_fn = value_fn

    @property
    def native_value(self):
        """Return the sensor value."""
        val = self.coordinator.data.get(self._json_key)
        if self._value_fn and val is not None:
            return self._value_fn(val)
        return val
