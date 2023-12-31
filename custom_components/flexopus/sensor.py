"""Sensor integration using DataUpdateCoordinator."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    BOOKABLE_TYPE_DESK,
    BOOKABLE_TYPE_MEETING_ROOM,
    BOOKABLE_TYPE_PARKING_SPACE,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

bookable_type_names = {
    BOOKABLE_TYPE_DESK: "Desk",
    BOOKABLE_TYPE_MEETING_ROOM: "Meeting Room",
    BOOKABLE_TYPE_PARKING_SPACE: "Parking Space",
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities,
):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(FlexopusSensor(coordinator, key) for key in coordinator.data)


class FlexopusSensor(CoordinatorEntity, BinarySensorEntity):
    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_name = "Occupancy"
    _attr_device_class = BinarySensorDeviceClass.OCCUPANCY

    data: dict = property(
        fget=lambda self: self.coordinator.data[self.coordinator_context]
    )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.coordinator_context not in self.coordinator.data:
            _LOGGER.error("Not found")
            return
        self.async_write_ha_state()

    @property
    def is_on(self) -> bool:
        return self.data["occupied"]

    @property
    def unique_id(self) -> str:
        return self.data["id"]

    @property
    def icon(self) -> str:
        # mdi:door, mdi:parking, https://pictogrammers.com/library/mdi/
        if self.data["type"] == BOOKABLE_TYPE_DESK:
            return "mdi:desk"
        if self.data["type"] == BOOKABLE_TYPE_PARKING_SPACE:
            return "mdi:parking"
        if self.data["type"] == BOOKABLE_TYPE_MEETING_ROOM:
            return "mdi:door"

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "booking_current": self.data.get("booking_current", None),
            "booking_next": self.data.get("booking_next", None),
        }

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.data["id"])},
            suggested_area=self.data["location_name"],
            name=f"{self.data['location_name']} {self.data['name']}",
            manufacturer="Flexopus",
            model=bookable_type_names.get(self.data["type"], "Unknown Type"),
            sw_version="1.0.0",
        )
