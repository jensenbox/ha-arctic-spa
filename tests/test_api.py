"""Tests for the Arctic Spa API client."""
from unittest.mock import AsyncMock, MagicMock
import sys
from types import ModuleType

# Stub out homeassistant modules so we can import api.py without HA installed
ha_mock = ModuleType("homeassistant")
ha_mock.config_entries = MagicMock()
ha_mock.const = MagicMock()
ha_mock.const.CONF_API_KEY = "api_key"
ha_mock.core = MagicMock()
ha_mock.helpers = MagicMock()
ha_mock.helpers.update_coordinator = MagicMock()
ha_mock.helpers.entity = MagicMock()
ha_mock.helpers.device_registry = MagicMock()
ha_mock.helpers.aiohttp_client = MagicMock()
ha_mock.helpers.entity_platform = MagicMock()
ha_mock.components = MagicMock()
for mod in [
    "homeassistant",
    "homeassistant.config_entries",
    "homeassistant.const",
    "homeassistant.core",
    "homeassistant.helpers",
    "homeassistant.helpers.update_coordinator",
    "homeassistant.helpers.entity",
    "homeassistant.helpers.device_registry",
    "homeassistant.helpers.aiohttp_client",
    "homeassistant.helpers.entity_platform",
    "homeassistant.components",
    "homeassistant.components.sensor",
    "homeassistant.components.binary_sensor",
    "homeassistant.components.switch",
    "homeassistant.components.number",
]:
    sys.modules.setdefault(mod, MagicMock())

import aiohttp
import pytest

from custom_components.arctic_spa.api import (
    ArcticSpaClient,
    ArcticSpaAuthError,
    ArcticSpaConnectionError,
    SpaStatus,
    LightState,
    PumpState,
)


MOCK_STATUS_RESPONSE = {
    "connected": True,
    "temperatureF": 100,
    "setpointF": 100,
    "lights": "off",
    "spaboy_connected": True,
    "spaboy_producing": False,
    "ph": 7.46,
    "ph_status": "OK",
    "orp": 553,
    "orp_status": "OK",
    "pump1": "off",
    "pump2": "off",
    "filter_status": "Idle",
    "filtration_duration": 1,
    "filtration_frequency": 1,
    "filter_suspension": "on",
    "errors": [],
}


class TestSpaStatus:
    """Tests for SpaStatus dataclass."""

    def test_from_dict(self):
        """Test creating SpaStatus from API response."""
        status = SpaStatus.from_dict(MOCK_STATUS_RESPONSE)
        assert status.connected is True
        assert status.temperature_f == 100
        assert status.setpoint_f == 100
        assert status.lights == "off"
        assert status.pump1 == "off"
        assert status.pump2 == "off"
        assert status.ph == 7.46
        assert status.ph_status == "OK"
        assert status.orp == 553
        assert status.filter_status == "Idle"
        assert status.filtration_duration == 1
        assert status.filtration_frequency == 1
        assert status.errors == []

    def test_from_dict_defaults(self):
        """Test defaults when keys are missing."""
        status = SpaStatus.from_dict({})
        assert status.connected is False
        assert status.temperature_f == 0
        assert status.lights == "off"
        assert status.errors == []


class TestArcticSpaClient:
    """Tests for the API client."""

    @pytest.fixture
    def mock_response(self):
        """Create a mock aiohttp response."""
        response = AsyncMock()
        response.status = 200
        response.json = AsyncMock(return_value=MOCK_STATUS_RESPONSE)
        return response

    @pytest.fixture
    def mock_session(self, mock_response):
        """Create a mock aiohttp session."""
        session = MagicMock(spec=aiohttp.ClientSession)
        session.closed = False

        # Mock context managers for get and put
        cm = AsyncMock()
        cm.__aenter__ = AsyncMock(return_value=mock_response)
        cm.__aexit__ = AsyncMock(return_value=False)

        session.get = MagicMock(return_value=cm)
        session.put = MagicMock(return_value=cm)

        return session

    @pytest.mark.asyncio
    async def test_get_status(self, mock_session):
        """Test getting spa status."""
        client = ArcticSpaClient("test_key", session=mock_session)
        status = await client.async_get_status()

        assert status.connected is True
        assert status.temperature_f == 100
        assert status.ph == 7.46

    @pytest.mark.asyncio
    async def test_get_status_raw(self, mock_session):
        """Test getting raw status dict."""
        client = ArcticSpaClient("test_key", session=mock_session)
        data = await client.async_get_status_raw()

        assert data == MOCK_STATUS_RESPONSE

    @pytest.mark.asyncio
    async def test_auth_error(self, mock_session, mock_response):
        """Test authentication error handling."""
        mock_response.status = 401
        client = ArcticSpaClient("bad_key", session=mock_session)

        with pytest.raises(ArcticSpaAuthError):
            await client.async_get_status()

    @pytest.mark.asyncio
    async def test_set_lights(self, mock_session):
        """Test setting lights."""
        client = ArcticSpaClient("test_key", session=mock_session)
        result = await client.async_set_lights(LightState.ON)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_pump(self, mock_session):
        """Test setting pump state."""
        client = ArcticSpaClient("test_key", session=mock_session)
        result = await client.async_set_pump(1, PumpState.HIGH)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_temperature(self, mock_session):
        """Test setting temperature."""
        client = ArcticSpaClient("test_key", session=mock_session)
        result = await client.async_set_temperature(102)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_filtration(self, mock_session):
        """Test setting filtration schedule."""
        client = ArcticSpaClient("test_key", session=mock_session)
        result = await client.async_set_filtration(2, 3)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_boost(self, mock_session):
        """Test setting boost mode."""
        client = ArcticSpaClient("test_key", session=mock_session)
        result = await client.async_set_boost(True)
        assert result is True

    @pytest.mark.asyncio
    async def test_validate_success(self, mock_session):
        """Test successful validation."""
        client = ArcticSpaClient("test_key", session=mock_session)
        result = await client.async_validate()
        assert result is True
