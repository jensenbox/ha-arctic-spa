"""Config flow for Arctic Spa integration."""
from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import ArcticSpaAuthError, ArcticSpaClient, ArcticSpaConnectionError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

_SCHEMA = vol.Schema({vol.Required(CONF_API_KEY): str})


class ArcticSpaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Arctic Spa."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            api_key = user_input[CONF_API_KEY]
            client = ArcticSpaClient(api_key, session=async_get_clientsession(self.hass))

            try:
                await client.async_get_status()

                # Prevent duplicate entries
                await self.async_set_unique_id(api_key[:16])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title="Arctic Spa",
                    data={CONF_API_KEY: api_key},
                )
            except ArcticSpaAuthError:
                errors["base"] = "invalid_auth"
            except ArcticSpaConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected error during config validation")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=_SCHEMA,
            errors=errors,
        )

    async def async_step_reauth(self, entry_data):
        """Handle re-authentication when the API key is invalid."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        """Handle re-authentication confirmation."""
        errors = {}

        if user_input is not None:
            api_key = user_input[CONF_API_KEY]
            client = ArcticSpaClient(api_key, session=async_get_clientsession(self.hass))

            try:
                await client.async_get_status()

                entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
                self.hass.config_entries.async_update_entry(
                    entry, data={CONF_API_KEY: api_key}
                )
                await self.hass.config_entries.async_reload(entry.entry_id)
                return self.async_abort(reason="reauth_successful")
            except ArcticSpaAuthError:
                errors["base"] = "invalid_auth"
            except ArcticSpaConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected error during reauth validation")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=_SCHEMA,
            errors=errors,
        )
