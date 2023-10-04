from homeassistant.core import HomeAssistant
from .api import Api
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
import logging
from .const import SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class DataCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, api: Api, location_ids) -> None:
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
                bookables[elem['id']] = elem

        return bookables
