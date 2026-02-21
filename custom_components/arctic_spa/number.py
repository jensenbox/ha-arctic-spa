"""Number platform for Arctic Spa."""
from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import ArcticSpaEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Arctic Spa number entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        ArcticSpaTemperature(coordinator, entry.entry_id),
        ArcticSpaFiltrationDuration(coordinator, entry.entry_id),
        ArcticSpaFiltrationFrequency(coordinator, entry.entry_id),
    ])


class ArcticSpaTemperature(ArcticSpaEntity, NumberEntity):
    """Number entity for spa temperature setpoint."""

    _attr_icon = "mdi:thermometer"
    _attr_native_min_value = 80
    _attr_native_max_value = 104
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "°F"
    _attr_mode = NumberMode.SLIDER

    def __init__(self, coordinator, entry_id):
        """Initialize the temperature control."""
        super().__init__(coordinator, entry_id, "temperature_setpoint", "Temperature Setpoint")

    @property
    def native_value(self) -> float | None:
        """Return the current setpoint."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("setpointF")

    async def async_set_native_value(self, value: float) -> None:
        """Set the temperature setpoint."""
        await self.coordinator.client.async_set_temperature(int(value))
        await self.coordinator.async_request_refresh()


class ArcticSpaFiltrationDuration(ArcticSpaEntity, NumberEntity):
    """Number entity for filtration duration."""

    _attr_icon = "mdi:timer-outline"
    _attr_native_min_value = 1
    _attr_native_max_value = 24
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "hr"
    _attr_mode = NumberMode.SLIDER

    def __init__(self, coordinator, entry_id):
        """Initialize the filtration duration control."""
        super().__init__(coordinator, entry_id, "filtration_duration_ctrl", "Filtration Duration")

    @property
    def native_value(self) -> float | None:
        """Return the current duration."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("filtration_duration")

    async def async_set_native_value(self, value: float) -> None:
        """Set filtration duration."""
        freq = self.coordinator.data.get("filtration_frequency", 1)
        await self.coordinator.client.async_set_filtration(int(value), int(freq))
        await self.coordinator.async_request_refresh()


class ArcticSpaFiltrationFrequency(ArcticSpaEntity, NumberEntity):
    """Number entity for filtration frequency."""

    _attr_icon = "mdi:refresh"
    _attr_native_min_value = 1
    _attr_native_max_value = 24
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "x/day"
    _attr_mode = NumberMode.SLIDER

    def __init__(self, coordinator, entry_id):
        """Initialize the filtration frequency control."""
        super().__init__(coordinator, entry_id, "filtration_frequency_ctrl", "Filtration Frequency")

    @property
    def native_value(self) -> float | None:
        """Return the current frequency."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("filtration_frequency")

    async def async_set_native_value(self, value: float) -> None:
        """Set filtration frequency."""
        dur = self.coordinator.data.get("filtration_duration", 1)
        await self.coordinator.client.async_set_filtration(int(dur), int(value))
        await self.coordinator.async_request_refresh()
