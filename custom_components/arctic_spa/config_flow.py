"""Config flow for Arctic Spa integration."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY

from .api import ArcticSpaAuthError, ArcticSpaClient, ArcticSpaConnectionError
from .const import DOMAIN


class ArcticSpaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Arctic Spa."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            api_key = user_input[CONF_API_KEY]
            client = ArcticSpaClient(api_key)

            try:
                await client.async_get_status()
                await client.close()

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
                errors["base"] = "unknown"
            finally:
                await client.close()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): str,
                }
            ),
            errors=errors,
        )
