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
        
        # No long-lived objects created on the event loop to avoid blocking
        self._initialized = True
        _LOGGER.debug("Wave client initialized for %s", self.serial_number)
    
    async def get_status(self) -> Optional[Dict[str, Any]]:
        """Get current thermostat status."""
        try:
            # Run the synchronous update in an executor
            loop = asyncio.get_event_loop()
            _LOGGER.debug("Wave client fetching status…")
            def _sync_status():
                import asyncio as _asyncio
                th_loop = _asyncio.new_event_loop()
                try:
                    _asyncio.set_event_loop(th_loop)
                    status = WaveStatus(
                        serial_number=self.serial_number,
                        access_code=self.access_code,
                        password=self.password,
                    )
                    status.update()
                    return status.data
                finally:
                    try:
                        th_loop.run_until_complete(th_loop.shutdown_asyncgens())
                    except Exception:
                        pass
                    _asyncio.set_event_loop(None)
                    th_loop.close()

            data = await loop.run_in_executor(None, _sync_status)
            if data:
                _LOGGER.debug("Wave client received data keys: %s", list(data.keys()))
                return dict(data)
            return None
            
        except Exception as e:
            _LOGGER.error("Failed to get status: %s", e)
            return None
    
    async def set_temperature(self, temperature: float) -> bool:
        """Set target temperature."""
        try:
            # Get current status to determine mode
            current = await self.get_status()
            
            loop = asyncio.get_event_loop()
            
            program_mode = None
            try:
                program_mode = current.get('UMD') if isinstance(current, dict) else None
            except Exception:
                program_mode = None

            if program_mode == MANUAL:
                # Manual mode - set manual temperature
                _LOGGER.debug("Setting manual temperature to %s", temperature)
                def _sync_set_manual():
                    import asyncio as _asyncio
                    th_loop = _asyncio.new_event_loop()
                    try:
                        _asyncio.set_event_loop(th_loop)
                        setter = WaveSet(
                            serial_number=self.serial_number,
                            access_code=self.access_code,
                            password=self.password,
                        )
                        return setter.post_message('heatingCircuits/hc1/temperatureRoomManual', temperature)
                    finally:
                        try:
                            th_loop.run_until_complete(th_loop.shutdown_asyncgens())
                        except Exception:
                            pass
                        _asyncio.set_event_loop(None)
                        th_loop.close()
                ok = await loop.run_in_executor(None, _sync_set_manual)
                if not ok:
                    return False
            else:
                _LOGGER.debug("Setting override temperature to %s and enabling override", temperature)
                # Auto mode - set override temperature
                def _sync_set_override_temp():
                    import asyncio as _asyncio
                    th_loop = _asyncio.new_event_loop()
                    try:
                        _asyncio.set_event_loop(th_loop)
                        setter = WaveSet(
                            serial_number=self.serial_number,
                            access_code=self.access_code,
                            password=self.password,
                        )
                        return setter.post_message('heatingCircuits/hc1/manualTempOverride/temperature', temperature)
                    finally:
                        try:
                            th_loop.run_until_complete(th_loop.shutdown_asyncgens())
                        except Exception:
                            pass
                        _asyncio.set_event_loop(None)
                        th_loop.close()
                ok = await loop.run_in_executor(None, _sync_set_override_temp)
                if not ok:
                    return False
                # Enable override
                def _sync_enable_override():
                    import asyncio as _asyncio
                    th_loop = _asyncio.new_event_loop()
                    try:
                        _asyncio.set_event_loop(th_loop)
                        setter = WaveSet(
                            serial_number=self.serial_number,
                            access_code=self.access_code,
                            password=self.password,
                        )
                        return setter.post_message('heatingCircuits/hc1/manualTempOverride/status', ON)
                    finally:
                        try:
                            th_loop.run_until_complete(th_loop.shutdown_asyncgens())
                        except Exception:
                            pass
                        _asyncio.set_event_loop(None)
                        th_loop.close()
                ok2 = await loop.run_in_executor(None, _sync_enable_override)
                if not ok2:
                    return False
            
            return True
            
        except Exception as e:
            _LOGGER.error("Failed to set temperature: %s", e)
            return False
    
    async def set_mode(self, mode: str) -> bool:
        """Set thermostat mode."""
        try:
            loop = asyncio.get_event_loop()
            
            # Map HA modes to Wave modes
            _LOGGER.debug("Setting mode: %s", mode)
            if mode == "heat":
                wave_mode = MANUAL
            elif mode == "auto":
                wave_mode = CLOCK
            elif mode == "off":
                # Turn off by setting very low temperature
                _LOGGER.debug("Setting off via low temperature")
                await self.set_temperature(5.0)
                return True
            else:
                _LOGGER.warning("Unknown mode: %s", mode)
                return False
            
            def _sync_set_mode():
                import asyncio as _asyncio
                th_loop = _asyncio.new_event_loop()
                try:
                    _asyncio.set_event_loop(th_loop)
                    setter = WaveSet(
                        serial_number=self.serial_number,
                        access_code=self.access_code,
                        password=self.password,
                    )
                    return setter.post_message('heatingCircuits/hc1/usermode', wave_mode)
                finally:
                    try:
                        th_loop.run_until_complete(th_loop.shutdown_asyncgens())
                    except Exception:
                        pass
                    _asyncio.set_event_loop(None)
                    th_loop.close()
            ok = await loop.run_in_executor(None, _sync_set_mode)
            if not ok:
                return False
            
            return True
            
        except Exception as e:
            _LOGGER.error("Failed to set mode: %s", e)
            return False
    
    async def close(self) -> None:
        """Close the client connection."""
        # Nothing persistent to close in this implementation
        self._initialized = False