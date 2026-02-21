"""Binary sensor platform for Arctic Spa."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import ArcticSpaEntity

BINARY_SENSORS = [
    # (key, name, device_class, icon, value_fn)
    (
        "connected",
        "Connected",
        BinarySensorDeviceClass.CONNECTIVITY,
        None,
        lambda d: d.get("connected", False),
    ),
    (
        "spaboy_connected",
        "SpaBoy Connected",
        BinarySensorDeviceClass.CONNECTIVITY,
        None,
        lambda d: d.get("spaboy_connected", False),
    ),
    (
        "spaboy_producing",
        "SpaBoy Producing",
        None,
        "mdi:chemical-weapon",
        lambda d: d.get("spaboy_producing", False),
    ),
    (
        "lights",
        "Lights",
        BinarySensorDeviceClass.LIGHT,
        None,
        lambda d: d.get("lights") == "on",
    ),
    (
        "filter_suspension",
        "Filter Suspension",
        None,
        "mdi:air-filter",
        lambda d: d.get("filter_suspension") == "on",
    ),
    (
        "pump1_running",
        "Pump 1 Running",
        BinarySensorDeviceClass.RUNNING,
        None,
        lambda d: d.get("pump1", "off") != "off",
    ),
    (
        "pump2_running",
        "Pump 2 Running",
        BinarySensorDeviceClass.RUNNING,
        None,
        lambda d: d.get("pump2", "off") != "off",
    ),
    (
        "has_errors",
        "Has Errors",
        BinarySensorDeviceClass.PROBLEM,
        None,
        lambda d: len(d.get("errors", [])) > 0,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Arctic Spa binary sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        ArcticSpaBinarySensor(coordinator, entry.entry_id, key, name, dev_cls, icon, value_fn)
        for key, name, dev_cls, icon, value_fn in BINARY_SENSORS
    )


class ArcticSpaBinarySensor(ArcticSpaEntity, BinarySensorEntity):
    """Representation of an Arctic Spa binary sensor."""

    def __init__(self, coordinator, entry_id, key, name, device_class, icon, value_fn):
        """Initialize the binary sensor."""
        super().__init__(coordinator, entry_id, key, name)
        self._attr_device_class = device_class
        self._attr_icon = icon
        self._value_fn = value_fn

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        if self.coordinator.data is None:
            return None
        return self._value_fn(self.coordinator.data)
