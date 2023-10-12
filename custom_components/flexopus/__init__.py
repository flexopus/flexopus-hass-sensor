"""Flexopus Component."""

import logging

from flexopus import FlexopusApi

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    CONF_ACCESS_TOKEN,
    CONF_TENANT_URL,
    DOMAIN,
    OPTION_LOCATIONS,
    PLATFORMS,
)
from .data_coordinator import DataCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up platform from a ConfigEntry."""
    hass.data.setdefault(DOMAIN, {})
    _LOGGER.debug(entry.as_dict())

    api = FlexopusApi(
        entry.data[CONF_TENANT_URL],
        entry.data[CONF_ACCESS_TOKEN],
    )
    locations = []
    if OPTION_LOCATIONS in entry.options:
        locations = entry.options[OPTION_LOCATIONS]
    coordinator = DataCoordinator(hass, api, locations)
    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = coordinator

    entry.async_on_unload(entry.add_update_listener(options_update_listener))

    # Forward the setup to the sensor platform.
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        del hass.data[DOMAIN]
    return unload_ok


async def options_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)
