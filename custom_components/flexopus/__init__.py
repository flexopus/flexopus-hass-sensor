"""Flexopus Component."""

import logging

import voluptuous as vol

from homeassistant import core, config_entries
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    CONF_ACCESS_TOKEN,
    CONF_PATH,
)
from .const import DOMAIN

from .api import Api
from .data_coordinator import DataCoordinator

_LOGGER = logging.getLogger(__name__)

CONF_TENANT_URL = "url"
CONF_SECURE = "secure"
CONF_LOCATION = "locations"
BUILDING_SCHEMA = vol.Schema({vol.Required(CONF_PATH): cv.string})


async def async_setup_entry(
        hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Set up platform from a ConfigEntry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data
    _LOGGER.warning(hass.data[DOMAIN][entry.entry_id])

    flexopus_api = Api(
        hass.data[DOMAIN][entry.entry_id][CONF_TENANT_URL],
        hass.data[DOMAIN][entry.entry_id][CONF_ACCESS_TOKEN]
    )
    coordinator = DataCoordinator(hass, flexopus_api, [1, 2])
    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Forward the setup to the sensor platform.
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True
