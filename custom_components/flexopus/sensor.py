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
    current_sensors = []

    # Create a callback function to update the sensors when the coordinator data changes
    def coordinator_data_update_callback():
        nonlocal current_sensors
        current_sensors_list = list(current_sensors)

        current_sensor_ids = set(key for key, _ in current_sensors_list)
        new_sensor_ids = set(key for key, _ in coordinator.data.items())

        # removed_items = [key for key, value in current_sensors_list if key not in new_sensor_ids]
        added_items = [
            key
            for key, value in coordinator.data.items()
            if key not in current_sensor_ids
        ]

        async_add_entities(
            (FlexopusSensor(coordinator, idx) for idx in added_items),
            update_before_add=True,
        )

        current_sensors = coordinator.data.items()

    coordinator.async_add_listener(coordinator_data_update_callback)


class FlexopusSensor(CoordinatorEntity, BinarySensorEntity):
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, coordinator, idx) -> None:
        super().__init__(coordinator, context=idx)
        self.idx = idx
        self.data = self.coordinator.data[self.idx]
        self.update_data()

    def update_data(self):
        self._attr_name = "Occupancy"
        self._attr_is_on = self.data["occupied"]
        self._attr_unique_id = self.data["id"]
        self._attr_device_class = BinarySensorDeviceClass.OCCUPANCY
        self._attr_extra_state_attributes = {"next_booking": None}
        # mdi:door, mdi:parking, https://pictogrammers.com/library/mdi/
        if self.data["type"] == 'Desk':
            self._attr_icon = "mdi:desk"
        if self.data["type"] == 'Parking_Space':
            self._attr_icon = "mdi:parking"
        if self.data["type"] == 'Meeting_Room':
            self._attr_icon = "mdi:door"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.idx not in self.coordinator.data:
            return

        self.data = self.coordinator.data[self.idx]
        self.update_data()

        _LOGGER.debug(self.idx)

        self.async_write_ha_state()

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.data["id"])},
            suggested_area=self.data["location_name"],
            name=self.data["location_name"] + " " + self.data["name"],
            manufacturer="Flexopus",
            model=self.data["type"],
            sw_version="1.0.0",
        )
