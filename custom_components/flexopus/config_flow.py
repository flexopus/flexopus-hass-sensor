"""Config flow to configure the Moon integration."""
from __future__ import annotations

from typing import Any, Dict
import voluptuous as vol
from aiohttp import ClientResponseError

from .api import Api
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv
from . import CONF_TENANT_URL

from .const import DOMAIN

AUTH_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ACCESS_TOKEN): cv.string,
        vol.Optional(CONF_TENANT_URL): cv.string,
    }
)


async def validate_auth(access_token: str, url: str) -> None:
    """Validates a GitHub access token.
    Raises a ValueError if the auth token is invalid.
    """
    api = Api(url, access_token)
    try:
        await api.fetch_buildings()
    except ClientResponseError:
        raise ValueError


class FlexopusConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the user."""
        # if self._async_current_entries():
        #    return self.async_abort(reason="single_instance_allowed")

        errors: Dict[str, str] = {}
        if user_input is not None:
            try:
                await validate_auth(
                    user_input[CONF_ACCESS_TOKEN], user_input[CONF_TENANT_URL]
                )
            except ValueError:
                errors["base"] = "auth"
            if not errors:
                # Input is valid, set data.
                self.data = user_input
                # Return the form of the next step.

                return self.async_create_entry(
                    title=DOMAIN,
                    data={
                        CONF_ACCESS_TOKEN: user_input[CONF_ACCESS_TOKEN],
                        CONF_TENANT_URL: user_input[CONF_TENANT_URL],
                    },
                )

        return self.async_show_form(
            step_id="user", data_schema=AUTH_SCHEMA, errors=errors
        )
