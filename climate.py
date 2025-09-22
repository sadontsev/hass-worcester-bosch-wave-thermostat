"""
Worcester Bosch Wave Climate Platform
Provides comprehensive climate control with all available metrics.
"""

import logging
from typing import Any

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    HVAC_MODE_AUTO,
    ClimateEntityFeature,
    HVACAction,
)
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    CONF_SERIAL_NUMBER,
    CONF_ACCESS_CODE,
    CONF_PASSWORD,
    MANUFACTURER,
    MODEL,
)
from .coordinator import WorcesterWaveDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Worcester Bosch Wave climate platform."""
    
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    
    _LOGGER.info("Setting up Worcester Bosch Wave climate entity")
    
    climate_entity = WorcesterWaveClimate(coordinator, config_entry)
    async_add_entities([climate_entity])


class WorcesterWaveClimate(CoordinatorEntity, ClimateEntity):
    """Worcester Bosch Wave Climate entity with comprehensive metrics."""

    def __init__(
        self,
        coordinator: WorcesterWaveDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator)
        
        self._serial_number = config_entry.data[CONF_SERIAL_NUMBER]
        
        # Entity properties
        self._attr_name = "Worcester Bosch Wave Thermostat"
        self._attr_unique_id = f"{DOMAIN}_{self._serial_number}"
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_precision = 0.1
        self._attr_min_temp = 5.0
        self._attr_max_temp = 35.0
        self._attr_target_temperature_step = 0.5
        
        # Supported features
        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.TURN_ON
            | ClimateEntityFeature.TURN_OFF
        )
        
        # HVAC modes
        self._attr_hvac_modes = [HVAC_MODE_OFF, HVAC_MODE_HEAT, HVAC_MODE_AUTO]

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._serial_number)},
            name="Worcester Bosch Wave Thermostat",
            manufacturer=MANUFACTURER,
            model=MODEL,
            sw_version="1.0",
        )

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        if not self.coordinator.data:
            return None
        
        current_temp = self.coordinator.data.get("IHT")
        if current_temp is not None:
            try:
                return float(current_temp)
            except (ValueError, TypeError):
                return None
        return None

    @property
    def target_temperature(self) -> float | None:
        """Return the target temperature."""
        if not self.coordinator.data:
            return None
            
        target_temp = self.coordinator.data.get("TSP")
        if target_temp is not None:
            try:
                return float(target_temp)
            except (ValueError, TypeError):
                return None
        return None

    @property
    def hvac_mode(self) -> str:
        """Return current hvac mode."""
        if not self.coordinator.data:
            return HVAC_MODE_OFF
            
        # Check system mode based on UMD (Program Mode) and other indicators
        umd = str(self.coordinator.data.get("UMD", "")).lower()
        bai = str(self.coordinator.data.get("BAI", "")).lower()
        
        # If boiler is not active, consider it off
        if bai in ["no", "false", "off", "0"]:
            return HVAC_MODE_OFF
            
        # Check program mode
        if umd in ["manual", "man"]:
            return HVAC_MODE_HEAT
        elif umd in ["auto", "automatic", "program", "prog"]:
            return HVAC_MODE_AUTO
        else:
            return HVAC_MODE_HEAT  # Default to heat mode

    @property
    def hvac_action(self) -> str:
        """Return current hvac action."""
        if not self.coordinator.data:
            return HVACAction.IDLE
            
        # Check if boiler is actively heating
        bai = str(self.coordinator.data.get("BAI", "")).lower()
        
        if bai in ["no", "false", "off", "0"]:
            return HVACAction.IDLE
        else:
            return HVACAction.HEATING

    async def async_set_temperature(self, **kwargs) -> None:
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
            
        _LOGGER.debug("Setting target temperature to %s", temperature)
        
        try:
            await self.coordinator.async_set_temperature(temperature)
        except Exception as err:
            _LOGGER.error("Failed to set temperature: %s", err)

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new hvac mode."""
        _LOGGER.debug("Setting HVAC mode to %s", hvac_mode)
        
        try:
            if hvac_mode == HVAC_MODE_OFF:
                await self.coordinator.async_set_mode("off")
            elif hvac_mode == HVAC_MODE_HEAT:
                await self.coordinator.async_set_mode("manual")
            elif hvac_mode == HVAC_MODE_AUTO:
                await self.coordinator.async_set_mode("auto")
        except Exception as err:
            _LOGGER.error("Failed to set HVAC mode: %s", err)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return comprehensive thermostat state attributes organized by category."""
        if not self.coordinator.data:
            return {}
            
        data = self.coordinator.data
        
        attrs = {
            # Core Temperature Metrics
            "current_temperature_raw": data.get("IHT"),
            "target_temperature_raw": data.get("TSP"),
            "manual_temperature": data.get("MMT"),
            "current_switch_point": data.get("CSP"),
            "schedule_temperature": data.get("TOT"),
            
            # System Status
            "program_mode": data.get("UMD"),
            "control_mode": data.get("CPM"),
            "boiler_status": data.get("BAI"),
            "system_health": data.get("IHS"),
            "program_running": data.get("PMR"),
            
            # Hot Water System
            "hot_water_demand": data.get("DHW"),
            "boiler_enabled": data.get("BLE"),
            "backup_boiler_enabled": data.get("BBE"),
            "maintenance_required": data.get("BMR"),
            
            # Override Control
            "override_duration": data.get("TOD"),
            "override_active": data.get("DOT"),
            
            # Schedule Information
            "schedule_point": data.get("ARS"),
            "program_remaining": data.get("PMR"),
            "current_time": data.get("CTD"),
            "time_remaining": data.get("CTR"),
            
            # Diagnostic Data
            "reset_status": data.get("RS"),
            "frost_protection": data.get("FPA"),
            "energy_saving": data.get("ESI"),
            "holiday_enabled": data.get("HED_EN"),
            "holiday_device": data.get("HED_DEV"),
            "first_aid_help": data.get("FAH"),
            
            # Device Information
            "serial_number": self._serial_number,
            "last_update": data.get("CTD"),
        }
        
        # Remove None values to keep the attributes clean
        return {k: v for k, v in attrs.items() if v is not None}

import logging
import asyncio
from typing import Any

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    HVAC_MODE_AUTO,
    ClimateEntityFeature,
    HVACAction,
)
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo

from .const import (
    DOMAIN,
    CONF_SERIAL_NUMBER,
    CONF_ACCESS_CODE,
    CONF_PASSWORD,
    MANUFACTURER,
    MODEL,
)
from .worcester_bosch_wave.status import WaveStatus
from .worcester_bosch_wave.set import WaveSet

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Worcester Bosch Wave climate platform."""
    
    serial_number = config_entry.data[CONF_SERIAL_NUMBER]
    access_code = config_entry.data[CONF_ACCESS_CODE]
    password = config_entry.data[CONF_PASSWORD]
    
    _LOGGER.info("Setting up Worcester Bosch Wave climate entity")
    
    climate_entity = WorcesterWaveClimate(serial_number, access_code, password)
    async_add_entities([climate_entity], True)


class WorcesterWaveClimate(ClimateEntity):
    """Worcester Bosch Wave climate entity with comprehensive functionality."""

    def __init__(self, serial_number: str, access_code: str, password: str):
        """Initialize the climate entity."""
        self._serial_number = serial_number
        self._access_code = access_code  
        self._password = password
        
        # Entity properties
        self._attr_name = "Worcester Wave Thermostat"
        self._attr_unique_id = f"{DOMAIN}_{serial_number}_climate"
        
        # Temperature attributes
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_target_temperature_step = 0.5
        self._attr_min_temp = 5.0
        self._attr_max_temp = 30.0
        
        # HVAC attributes
        self._attr_hvac_modes = [HVAC_MODE_OFF, HVAC_MODE_HEAT, HVAC_MODE_AUTO]
        self._attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
        
        # State attributes
        self._attr_current_temperature = None
        self._attr_target_temperature = None
        self._attr_hvac_mode = None
        self._attr_hvac_action = None
        
        # Raw thermostat data for use by sensors
        self._last_data = None
        
        _LOGGER.info(f"Initialized Worcester Bosch Wave climate entity for {serial_number}")

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._serial_number)},
            name="Worcester Bosch Wave Thermostat",
            manufacturer=MANUFACTURER,
            model=MODEL,
            sw_version="1.0",
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes with all thermostat data."""
        if not self._last_data:
            return {}
            
        # Organize data into logical groups
        attributes = {
            # Core temperature data
            "current_temperature_raw": self._last_data.get("IHT"),
            "target_temperature_raw": self._last_data.get("TSP"),
            "manual_temperature": self._last_data.get("MMT"),
            "switch_point_temperature": self._last_data.get("CSP"),
            
            # System status
            "program_mode": self._last_data.get("UMD"),
            "boiler_status": self._last_data.get("BAI"),
            "system_health": self._last_data.get("IHS"),
            "control_mode": self._last_data.get("CPM"),
            
            # Hot water and comfort
            "hot_water_enabled": self._last_data.get("DHW"),
            "holiday_mode": self._last_data.get("HMD"),
            
            # Override and manual control
            "temperature_override": self._last_data.get("TOR"),
            "override_duration": self._last_data.get("TOD"),
            
            # Schedule and time
            "system_time": self._last_data.get("CTD"),
            "current_time_remaining": self._last_data.get("CTR"),
            "day_as_sunday": self._last_data.get("DAS"),
            "tomorrow_as_sunday": self._last_data.get("TAS"),
            
            # Advanced metrics
            "program_remaining": self._last_data.get("PMR"),
            "schedule_temperature": self._last_data.get("TOT"),
            
            # System information
            "connection_status": "connected" if self._last_data else "disconnected",
            "last_update": self._last_data.get("CTD", "unknown"),
        }
        
        # Add unknown/diagnostic metrics
        diagnostic_keys = ["ARS", "FPA", "ESI", "BLE", "BBE", "BMR", "RS", 
                          "HED_EN", "HED_DEV", "FAH", "DOT", "HED_DB"]
        for key in diagnostic_keys:
            if key in self._last_data:
                attributes[f"diagnostic_{key.lower()}"] = self._last_data[key]
        
        return attributes

    async def async_update(self) -> None:
        """Fetch new state data for the thermostat."""
        try:
            _LOGGER.debug("Updating Worcester Bosch Wave thermostat data")
            
            # Create status client to get current data
            status_client = WaveStatus(self._serial_number, self._access_code, self._password)
            
            # Run the update in an executor to avoid blocking
            await self.hass.async_add_executor_job(status_client.update)
            
            if status_client.data:
                self._last_data = status_client.data
                
                # Update temperature values
                if "IHT" in status_client.data:
                    self._attr_current_temperature = float(status_client.data["IHT"])
                if "TSP" in status_client.data:
                    self._attr_target_temperature = float(status_client.data["TSP"])
                
                # Update HVAC mode based on program mode
                program_mode = status_client.data.get("UMD", "").lower()
                if program_mode == "manual":
                    self._attr_hvac_mode = HVAC_MODE_HEAT
                elif program_mode == "clock":
                    self._attr_hvac_mode = HVAC_MODE_AUTO
                else:
                    self._attr_hvac_mode = HVAC_MODE_OFF
                
                # Update HVAC action based on boiler status
                boiler_status = status_client.data.get("BAI", "No")
                if boiler_status in ["CH", "HW"]:
                    self._attr_hvac_action = HVACAction.HEATING
                elif self._attr_hvac_mode == HVAC_MODE_OFF:
                    self._attr_hvac_action = HVACAction.OFF
                else:
                    self._attr_hvac_action = HVACAction.IDLE
                
                _LOGGER.debug(
                    f"Updated thermostat: temp={self._attr_current_temperature}°C, "
                    f"target={self._attr_target_temperature}°C, "
                    f"mode={self._attr_hvac_mode}, action={self._attr_hvac_action}"
                )
            else:
                _LOGGER.warning("Failed to get thermostat data")
                
        except Exception as e:
            _LOGGER.error(f"Error updating Worcester Bosch Wave thermostat: {e}")

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        
        if temperature is None:
            _LOGGER.error("No temperature provided")
            return
            
        try:
            _LOGGER.info(f"Setting temperature to {temperature}°C")
            
            # Create set client to change temperature
            set_client = WaveSet(self._serial_number, self._access_code, self._password)
            
            # Run the temperature set in an executor to avoid blocking
            await self.hass.async_add_executor_job(set_client.set_temperature, temperature)
            
            # Update the target temperature immediately for responsive UI
            self._attr_target_temperature = temperature
            
            # Schedule an update to get the latest state
            await self.async_update()
            
        except Exception as e:
            _LOGGER.error(f"Error setting temperature: {e}")

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        try:
            _LOGGER.info(f"Setting HVAC mode to {hvac_mode}")
            
            if hvac_mode == HVAC_MODE_OFF:
                # Turn off heating - set very low temperature
                await self.async_set_temperature(temperature=5.0)
            elif hvac_mode == HVAC_MODE_HEAT:
                # Manual mode - keep current target temperature
                pass  # Current target temp will be maintained
            elif hvac_mode == HVAC_MODE_AUTO:
                # Clock/schedule mode - would need schedule implementation
                _LOGGER.warning("Auto mode not fully implemented yet")
                
            self._attr_hvac_mode = hvac_mode
            
        except Exception as e:
            _LOGGER.error(f"Error setting HVAC mode: {e}")