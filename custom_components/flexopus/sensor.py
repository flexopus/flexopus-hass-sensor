"""Sensor integration using DataUpdateCoordinator."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
        hass: HomeAssistant,
        config: ConfigType,
        async_add_entities: AddEntitiesCallback,
        discovery_info: DiscoveryInfoType | None = None,
) -> None:
    coordinator = hass.data[DOMAIN]["coordinator"]

    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        (
            FlexopusSensor(coordinator, idx)
            for idx, ent in coordinator.data.items()
        ),
        update_before_add=True,
    )


class FlexopusSensor(CoordinatorEntity, BinarySensorEntity):
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, coordinator, idx) -> None:
        super().__init__(coordinator, context=idx)
        self.idx = idx
        self.data = self.coordinator.data[self.idx]
        self.update_data()

    def update_data(self):
        self._attr_name = self.data["name"]
        self._attr_is_on = self.data["occupied"]
        self._attr_unique_id = self.data["id"]
        self._attr_device_class = BinarySensorDeviceClass.OCCUPANCY

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.data = self.coordinator.data[self.idx]
        self.update_data()

        self.async_write_ha_state()
