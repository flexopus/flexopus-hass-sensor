"""Config flow to configure the Moon integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from aiohttp import ClientResponseError, InvalidURL, ClientConnectorError

import homeassistant.helpers.config_validation as cv
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .api import Api
from .const import CONF_ENTRY_TITLE, CONF_TENANT_URL, DOMAIN
from .options_flow import FlexopusOptionsFlow

AUTH_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_ENTRY_TITLE, default='Flexopus'): cv.string,
        vol.Required(CONF_ACCESS_TOKEN): cv.string,
        vol.Required(CONF_TENANT_URL): cv.string,
    }
)

_LOGGER = logging.getLogger(__name__)


class FlexopusConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:

        errors: dict[str, str] = {}
        if user_input is not None:
            api = Api(user_input[CONF_TENANT_URL], user_input[CONF_ACCESS_TOKEN])
            try:
                await api.fetch_buildings()
            except ClientResponseError:
                errors["base"] = "auth"
            except InvalidURL:
                errors["base"] = "invalid_url"
            except ClientConnectorError:
                errors["base"] = "cannot_connect"
            if not errors:
                return self.async_create_entry(
                    title=user_input.get(CONF_ENTRY_TITLE, 'Flexopus'),
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user", data_schema=AUTH_SCHEMA, errors=errors
        )


    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return FlexopusOptionsFlow(config_entry)


