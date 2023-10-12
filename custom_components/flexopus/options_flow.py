import logging
from typing import Any

import voluptuous as vol
from aiohttp import ClientConnectorError, ClientResponseError, InvalidURL
from flexopus import FlexopusApi

import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigEntry, OptionsFlow
from homeassistant.data_entry_flow import FlowResult

from . import OPTION_LOCATIONS
from .const import CONF_ACCESS_TOKEN, CONF_TENANT_URL

_LOGGER = logging.getLogger(__name__)


class FlexopusOptionsFlow(OptionsFlow):
    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self.all_locations = dict()

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        _LOGGER.debug(user_input)
        if user_input is not None:
            return self.async_create_entry(
                data={
                    OPTION_LOCATIONS: user_input[OPTION_LOCATIONS],
                },
            )
        try:
            errors = dict[str, str]()
            api = FlexopusApi(
                self.config_entry.data[CONF_TENANT_URL],
                self.config_entry.data[CONF_ACCESS_TOKEN],
            )
            available_locations = await api.get_locations()
            selected_locations = self.config_entry.options.get(OPTION_LOCATIONS, [])
            previous_count = len(selected_locations)
            selected_locations = [
                str(id) for id in selected_locations if str(id) in available_locations
            ]
            if len(selected_locations) < previous_count:
                errors["base"] = "invalid_location"
            return self.async_show_form(
                step_id="init",
                errors=errors,
                data_schema=vol.Schema(
                    {
                        vol.Optional(
                            OPTION_LOCATIONS, default=selected_locations
                        ): cv.multi_select(available_locations),
                    }
                ),
            )
        except (ClientResponseError, InvalidURL) as e:
            _LOGGER.error(e)
            return self.async_abort(reason="invalid_auth")
        except ClientConnectorError as e:
            _LOGGER.error(e)
            return self.async_abort(reason="cannot_connect")
        except Exception as e:  # pylance Broad
            _LOGGER.error(e)
            return self.async_abort(reason="unknown")
