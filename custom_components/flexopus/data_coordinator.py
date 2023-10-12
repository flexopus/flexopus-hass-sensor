import logging

from flexopus import FlexopusApi

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class DataCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, api: FlexopusApi, location_ids) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.api = api
        self.location_ids = location_ids

    async def _async_update_data(self):
        bookables = {}
        for location_id in self.location_ids:
            data = await self.api.fetch_location(location_id)
            for elem in data["data"]:
                bookables[elem["id"]] = elem
        return bookables

    def update(self, location_ids) -> None:
        self.location_ids = location_ids
