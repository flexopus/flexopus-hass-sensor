"""Flexopus Component."""

import logging

import voluptuous as vol

from homeassistant import core
from homeassistant.helpers.discovery import async_load_platform
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    CONF_ACCESS_TOKEN,
    CONF_PATH,
    CONF_URL,
)
from .const import DOMAIN

from .api import Api
from .const import BASE_API_URL
from .data_coordinator import DataCoordinator

_LOGGER = logging.getLogger(__name__)

CONF_LOCATION = "locations"
BUILDING_SCHEMA = vol.Schema({vol.Required(CONF_PATH): cv.string})

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_ACCESS_TOKEN): cv.string,
                vol.Required(CONF_LOCATION): cv.ensure_list,
                vol.Optional(CONF_URL): cv.url,
            }
        )
    },
    # The full HA configurations gets passed to `async_setup` so we need to allow
    # extra keys.
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Set up the platform.
    :returns: A boolean to indicate that initialization was successful.
    """
    conf = config[DOMAIN]

    api = Api(
        BASE_API_URL,
        conf[CONF_ACCESS_TOKEN],
    )

    coordinator = DataCoordinator(hass, api, conf[CONF_LOCATION])

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_refresh()

    hass.data[DOMAIN] = {
        "conf": config,
        "coordinator": coordinator,
    }
    hass.async_create_task(async_load_platform(hass, "sensor", DOMAIN, {}, conf))
    return True
