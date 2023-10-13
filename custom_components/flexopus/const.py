from datetime import timedelta

from homeassistant.const import Platform

DOMAIN = "flexopus"
SCAN_INTERVAL = timedelta(seconds=60)

CONF_ACCESS_TOKEN = "access_token"
CONF_ENTRY_TITLE = "entry_title"
CONF_TENANT_URL = "tenant_url"
OPTION_LOCATIONS = "locations"
PLATFORMS = [Platform.SENSOR]

BOOKABLE_TYPE_DESK = 0
BOOKABLE_TYPE_PARKING_SPACE = 1
BOOKABLE_TYPE_MEETING_ROOM = 2
BOOKABLE_TYPE_HOME_OFFICE = 3
