"""The Worcester Bosch Wave integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    CONF_SERIAL_NUMBER,
    CONF_ACCESS_CODE,
    CONF_PASSWORD,
)
from .coordinator import WorcesterWaveDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.CLIMATE, Platform.SENSOR, Platform.BINARY_SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Worcester Bosch Wave from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    # Create data update coordinator
    coordinator = WorcesterWaveDataUpdateCoordinator(
        hass,
        serial_number=entry.data[CONF_SERIAL_NUMBER],
        access_code=entry.data[CONF_ACCESS_CODE],
        password=entry.data[CONF_PASSWORD],
    )

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
    }

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        # Shutdown coordinator properly
        coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
        await coordinator.async_shutdown()
        
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
