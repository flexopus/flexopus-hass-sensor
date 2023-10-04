"""Config flow to configure the Moon integration."""
from __future__ import annotations

from typing import Any
import voluptuous as vol
from aiohttp import ClientResponseError

import logging
from homeassistant import config_entries
from homeassistant.core import callback

from homeassistant.helpers import selector

from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv
from . import CONF_TENANT_URL, OPTION_LOCATIONS

from .api import Api
from .options_flow import FlexopusOptionsFlow
from .const import DOMAIN

# TODO remove defaults
AUTH_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ACCESS_TOKEN, default='27|ieLdgZRVimqD8dmTO1f4FKe0ZKb0umqC1Bn0UUgr'): cv.string,
        vol.Required(CONF_TENANT_URL, default='http://test.flexopus.xyz'): cv.string,
    }
)

_LOGGER = logging.getLogger(__name__)


class FlexopusConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        # if self._async_current_entries():
        #    return self.async_abort(reason="single_instance_allowed")

        errors: dict[str, str] = {}
        if user_input is not None:
            api = Api(user_input[CONF_TENANT_URL], user_input[CONF_ACCESS_TOKEN])
            try:
                await api.fetch_buildings()
            except ClientResponseError:
                errors["base"] = "auth"
            if not errors:
                return self.async_create_entry(
                    title=DOMAIN,
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


