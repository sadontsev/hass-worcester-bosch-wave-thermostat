from homeassistant import config_entries

from constants import DOMAIN


class WorcesterWaveConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Example config flow."""

    pass
