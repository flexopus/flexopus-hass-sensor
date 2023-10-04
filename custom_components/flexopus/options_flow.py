import logging
from typing import Any
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
import voluptuous as vol
from . import OPTION_LOCATIONS, DOMAIN
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)


class FlexopusOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self.all_locations = dict()

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        _LOGGER.debug(self.config_entry.as_dict())
        if user_input is not None:
            return self.async_create_entry(
                data={
                    OPTION_LOCATIONS: user_input[OPTION_LOCATIONS],
                },
            )

        selected_locations = self.config_entry.options[OPTION_LOCATIONS] if OPTION_LOCATIONS in self.config_entry.options else []

        return self.async_show_form(
            step_id='init',
            data_schema=vol.Schema(
                {
                    vol.Optional(OPTION_LOCATIONS, default=selected_locations): cv.multi_select(
                        [1,2,3,4,5]
                    ),
                }
            ),
        )