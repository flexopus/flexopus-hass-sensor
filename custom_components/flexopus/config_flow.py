"""Config flow to configure the Moon integration."""
from __future__ import annotations

from typing import Any
import voluptuous as vol
from aiohttp import ClientResponseError

import logging

from homeassistant.helpers import selector

from .api import Api
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv
from . import CONF_TENANT_URL, CONF_LOCATION

from .const import DOMAIN

# TODO remove defaults
AUTH_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ACCESS_TOKEN, default='27|ieLdgZRVimqD8dmTO1f4FKe0ZKb0umqC1Bn0UUgr'): cv.string,
        vol.Optional(CONF_TENANT_URL, default='http://test.flexopus.xyz'): cv.string,
    }
)

_LOGGER = logging.getLogger(__name__)


class FlexopusConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1
    api = None
    all_locations: dict[str, str] = dict()
    data = dict()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        # if self._async_current_entries():
        #    return self.async_abort(reason="single_instance_allowed")

        errors: dict[str, str] = {}
        if user_input is not None:
            self.api = Api(user_input[CONF_TENANT_URL], user_input[CONF_ACCESS_TOKEN])
            try:
                buildings = await self.api.fetch_buildings()
                self.all_locations = {
                    l['id']: b['name'] + ' - ' + l['name']
                        for b in buildings['data']
                            for l in b['locations']
                }
                self.data = {
                    CONF_ACCESS_TOKEN: user_input[CONF_ACCESS_TOKEN],
                    CONF_TENANT_URL: user_input[CONF_TENANT_URL],
                }
                _LOGGER.debug(self.all_locations)
            except ClientResponseError:
                errors["base"] = "auth"
            if not errors:
                return await self.async_step_locations()

        return self.async_show_form(
            step_id="user", data_schema=AUTH_SCHEMA, errors=errors
        )

    async def async_step_locations(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        _LOGGER.debug(user_input)
        if not user_input:
            return self.async_show_form(
                step_id='locations',
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_LOCATION): cv.multi_select(
                            list(self.all_locations.keys())
                        ),
                    }
                ),
            )
        self.data[CONF_LOCATION] = user_input[CONF_LOCATION]
        return self.async_create_entry(
            title=DOMAIN,
            data=self.data,
        )


