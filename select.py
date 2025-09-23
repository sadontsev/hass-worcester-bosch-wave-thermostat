"""
Select platform to switch Worcester Bosch Wave program mode (manual/clock).
"""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    CONF_SERIAL_NUMBER,
)
from .coordinator import WorcesterWaveDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


OPTIONS = ["manual", "clock"]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: WorcesterWaveDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id][
        "coordinator"
    ]
    async_add_entities([WorcesterWaveModeSelect(coordinator, config_entry)])


class WorcesterWaveModeSelect(CoordinatorEntity, SelectEntity):
    """Select entity to choose between manual and clock modes."""

    _attr_icon = "mdi:thermostat"  # simple icon for visibility

    def __init__(
        self,
        coordinator: WorcesterWaveDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator)
        self._serial_number = config_entry.data[CONF_SERIAL_NUMBER]
        self._attr_name = "Wave Program Mode"
        self._attr_unique_id = f"{DOMAIN}_{self._serial_number}_mode"
        self._attr_options = OPTIONS

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._serial_number)},
            name="Worcester Bosch Wave Thermostat",
        )

    @property
    def current_option(self) -> str | None:
        data = self.coordinator.data or {}
        umd = str(data.get("UMD", "")).lower()
        if umd in ("manual", "clock"):
            return umd
        # Map common synonyms
        if umd in ("auto", "automatic", "program", "prog"):
            return "clock"
        return "manual"

    async def async_select_option(self, option: str) -> None:
        opt = option.lower().strip()
        if opt not in OPTIONS:
            _LOGGER.warning("Unknown program mode option: %s", option)
            return
        # Map to client modes
        mode = "heat" if opt == "manual" else "auto"
        ok = await self.coordinator.async_set_mode(mode)
        if not ok:
            _LOGGER.error("Failed to set program mode to %s", option)
        else:
            await self.coordinator.async_request_refresh()
