"""Data update coordinator for Arctic Spa."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ArcticSpaApiError, ArcticSpaClient
from .const import SCAN_INTERVAL_SECONDS

_LOGGER = logging.getLogger(__name__)


class ArcticSpaCoordinator(DataUpdateCoordinator[dict]):
    """Coordinator to poll the Arctic Spa API."""

    def __init__(self, hass: HomeAssistant, client: ArcticSpaClient) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Arctic Spa",
            update_interval=timedelta(seconds=SCAN_INTERVAL_SECONDS),
        )
        self.client = client

    async def _async_update_data(self) -> dict:
        """Fetch data from the API."""
        try:
            return await self.client.async_get_status_raw()
        except ArcticSpaApiError as err:
            raise UpdateFailed(str(err)) from err
