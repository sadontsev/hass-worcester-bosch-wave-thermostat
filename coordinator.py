"""
Data update coordinator for Worcester Bosch Wave thermostat.
"""

import asyncio
import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .worcester_bosch_wave.wave_thermo import WorcesterWaveClient

_LOGGER = logging.getLogger(__name__)

# Update interval - thermostat data doesn't change very frequently
UPDATE_INTERVAL = timedelta(seconds=30)


class WorcesterWaveDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from Worcester Bosch Wave thermostat."""

    def __init__(
        self,
        hass: HomeAssistant,
        serial_number: str,
        access_code: str,
        password: str,
    ) -> None:
        """Initialize the coordinator."""
        self.serial_number = serial_number
        self.access_code = access_code
        self.password = password
        self._client = None
        
        super().__init__(
            hass,
            _LOGGER,
            name="Worcester Bosch Wave",
            update_interval=UPDATE_INTERVAL,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the thermostat."""
        try:
            if self._client is None:
                self._client = WorcesterWaveClient(
                    serial_number=self.serial_number,
                    access_code=self.access_code,
                    password=self.password,
                )
                await self._client.initialize()

            # Get status data
            status_data = await self._client.get_status()
            
            if not status_data:
                _LOGGER.warning("No data received from thermostat")
                return {}
                
            _LOGGER.debug("Received thermostat data: %s", status_data)
            return status_data
            
        except Exception as err:
            _LOGGER.error("Error communicating with thermostat: %s", err)
            raise UpdateFailed(f"Error communicating with thermostat: {err}") from err

    async def async_set_temperature(self, temperature: float) -> bool:
        """Set target temperature."""
        try:
            if self._client is None:
                raise UpdateFailed("Client not initialized")
                
            success = await self._client.set_temperature(temperature)
            if success:
                # Trigger immediate update to reflect changes
                await self.async_request_refresh()
            return success
            
        except Exception as err:
            _LOGGER.error("Error setting temperature: %s", err)
            raise UpdateFailed(f"Error setting temperature: {err}") from err

    async def async_set_mode(self, mode: str) -> bool:
        """Set thermostat mode."""
        try:
            if self._client is None:
                raise UpdateFailed("Client not initialized")
                
            success = await self._client.set_mode(mode)
            if success:
                # Trigger immediate update to reflect changes
                await self.async_request_refresh()
            return success
            
        except Exception as err:
            _LOGGER.error("Error setting mode: %s", err)
            raise UpdateFailed(f"Error setting mode: {err}") from err

    async def async_shutdown(self) -> None:
        """Clean shutdown of the coordinator."""
        if self._client:
            await self._client.close()
            self._client = None