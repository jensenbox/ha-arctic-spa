"""Base entity for Arctic Spa."""

from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ArcticSpaCoordinator


class ArcticSpaEntity(CoordinatorEntity[ArcticSpaCoordinator]):
    """Base class for Arctic Spa entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ArcticSpaCoordinator,
        entry_id: str,
        key: str,
        name: str,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_{key}"
        self._attr_name = name
        self._entry_id = entry_id

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info to link this entity to the spa device."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry_id)},
            name="Arctic Spa",
            manufacturer="Arctic Spas",
            model="McKinley",
        )
