import logging
from urllib.parse import urlparse, urlunparse

import aiohttp

_LOGGER = logging.getLogger(__name__)


class Api:
    def __init__(self, tenant_url, access_token):
        self.base_url = self.normalize_url(tenant_url)
        self.access_token = access_token

    def get_header(self):
        return {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }

    async def fetch_location(self, location_id):
        headers = self.get_header()

        url = f"{self.base_url}/locations/{location_id}/bookables/occupancy"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                return await response.json()

    async def fetch_buildings(self):
        headers = self.get_header()

        url = f"{self.base_url}/buildings"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                return await response.json()

    def normalize_url(self, tenant_url):
        tenant_url = tenant_url.strip()
        parsed_url = urlparse(tenant_url)

        return urlunparse(
            (parsed_url.scheme, parsed_url.netloc, "/api/v1", None, None, None)
        )
