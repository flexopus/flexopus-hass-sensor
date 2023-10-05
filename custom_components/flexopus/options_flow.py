import logging
from typing import Any

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from . import OPTION_LOCATIONS
from .api import Api
from .const import CONF_ACCESS_TOKEN, CONF_TENANT_URL


class FlexopusOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self.all_locations = dict()

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(
                data={
                    OPTION_LOCATIONS: user_input[OPTION_LOCATIONS],
                },
            )

        api = Api(self.config_entry.data[CONF_TENANT_URL], self.config_entry.data[CONF_ACCESS_TOKEN])
        available_locations = await api.get_locations()
        selected_locations = self.config_entry.options[OPTION_LOCATIONS] if OPTION_LOCATIONS in self.config_entry.options else [10]
        selected_locations = [str(id) for id in selected_locations if str(id) in available_locations]

        return self.async_show_form(
            step_id='init',
            data_schema=vol.Schema(
                {
                    vol.Optional(OPTION_LOCATIONS, default=selected_locations): cv.multi_select(
                        available_locations
                    ),
                }
            ),
        )