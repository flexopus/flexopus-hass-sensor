from .api import Api
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
import logging
from .const import SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class DataCoordinator(DataUpdateCoordinator):
    bookables: dict[str, object] = {}

    def __init__(self, hass, api: Api, location_ids) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
            update_method=self.update_method,
        )
        self.api = api
        self.location_ids = location_ids

    async def update_method(self):
        self.bookables = {}
        for idx, ent in enumerate(self.location_ids):
            data = await self.api.fetch_location(ent)
            for elem in data["data"]:
                self.bookables[elem["id"]] = elem

        return self.bookables
