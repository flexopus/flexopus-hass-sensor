"""Sensor integration using DataUpdateCoordinator."""
from __future__ import annotations

import logging

from homeassistant import config_entries
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)
from homeassistant.core import HomeAssistant
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        FlexopusSensor(coordinator, key) for key in coordinator.data
    )


class FlexopusSensor(CoordinatorEntity, BinarySensorEntity):
    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_name = "Occupancy"
    _attr_device_class = BinarySensorDeviceClass.OCCUPANCY

    def __init__(self, coordinator, context) -> None:
        super().__init__(coordinator, context)
        self.update()

    def update(self):
        data = self.coordinator.data[self.coordinator_context]

        self._attr_is_on = data["occupied"]
        self._attr_unique_id = data["id"]
        self._attr_extra_state_attributes = {
            "current_booking_end": data['current_booking_end'],
            "next_booking_start": data['next_booking_start'],
        }
        if data['name'] == 'Jakuzzi':
            _LOGGER.debug(data)
        # mdi:door, mdi:parking, https://pictogrammers.com/library/mdi/
        if data["type"] == 'Desk':
            self._attr_icon = "mdi:desk"
        if data["type"] == 'Parking_Space':
            self._attr_icon = "mdi:parking"
        if data["type"] == 'Meeting_Room':
            self._attr_icon = "mdi:door"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.coordinator_context not in self.coordinator.data:
            _LOGGER.error('Not found')
            return

        self.update()
        self.async_write_ha_state()

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        data = self.coordinator.data[self.coordinator_context]
        return DeviceInfo(
            identifiers={(DOMAIN, data["id"])},
            suggested_area=data["location_name"],
            name=data["location_name"] + " " + data["name"],
            manufacturer="Flexopus",
            model=data["type"],
            sw_version="1.0.0",
        )
