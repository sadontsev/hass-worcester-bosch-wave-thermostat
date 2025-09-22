"""
Worcester Wave Thermostat Client
Async wrapper for Worcester Bosch Wave library.
"""

import asyncio
import logging
from typing import Optional, Dict, Any

from .status import WaveStatus
from .set import WaveSet
from .constants import MANUAL, CLOCK, ON, OFF

_LOGGER = logging.getLogger(__name__)


class WorcesterWaveClient:
    """Async client for Worcester Bosch Wave thermostat."""
    
    def __init__(self, serial_number: str, access_code: str, password: str):
        """Initialize the client."""
        self.serial_number = serial_number
        self.access_code = access_code
        self.password = password
        
        self._status = None
        self._setter = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the client."""
        if not self._initialized:
            self._status = WaveStatus(
                serial_number=self.serial_number,
                access_code=self.access_code,
                password=self.password
            )
            self._setter = WaveSet(
                serial_number=self.serial_number,
                access_code=self.access_code,
                password=self.password
            )
            self._initialized = True
    
    async def get_status(self) -> Optional[Dict[str, Any]]:
        """Get current thermostat status."""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Run the synchronous update in an executor
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._status.update)
            
            if self._status.data:
                return dict(self._status.data)
            return None
            
        except Exception as e:
            _LOGGER.error("Failed to get status: %s", e)
            return None
    
    async def set_temperature(self, temperature: float) -> bool:
        """Set target temperature."""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Get current status to determine mode
            await self.get_status()
            
            loop = asyncio.get_event_loop()
            
            if hasattr(self._status, 'program_mode') and self._status.program_mode == MANUAL:
                # Manual mode - set manual temperature
                await loop.run_in_executor(
                    None,
                    self._setter.post_message,
                    'heatingCircuits/hc1/temperatureRoomManual',
                    temperature
                )
            else:
                # Auto mode - set override temperature
                await loop.run_in_executor(
                    None,
                    self._setter.post_message,
                    'heatingCircuits/hc1/manualTempOverride/temperature',
                    temperature
                )
                # Enable override
                await loop.run_in_executor(
                    None,
                    self._setter.post_message,
                    'heatingCircuits/hc1/manualTempOverride/status',
                    ON
                )
            
            return True
            
        except Exception as e:
            _LOGGER.error("Failed to set temperature: %s", e)
            return False
    
    async def set_mode(self, mode: str) -> bool:
        """Set thermostat mode."""
        if not self._initialized:
            await self.initialize()
        
        try:
            loop = asyncio.get_event_loop()
            
            # Map HA modes to Wave modes
            if mode == "heat":
                wave_mode = MANUAL
            elif mode == "auto":
                wave_mode = CLOCK
            elif mode == "off":
                # Turn off by setting very low temperature
                await self.set_temperature(5.0)
                return True
            else:
                _LOGGER.warning("Unknown mode: %s", mode)
                return False
            
            await loop.run_in_executor(
                None,
                self._setter.post_message,
                'heatingCircuits/hc1/usermode',
                wave_mode
            )
            
            return True
            
        except Exception as e:
            _LOGGER.error("Failed to set mode: %s", e)
            return False
    
    async def close(self) -> None:
        """Close the client connection."""
        # Nothing to close for this implementation
        self._initialized = False
        self._status = None
        self._setter = None