"""
Worcester Bosch Wave Climate Platform
Provides comprehensive climate control with all available metrics.
"""

import logging
from typing import Any

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import HVACMode, ClimateEntityFeature, HVACAction
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
        self._attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
        
        # HVAC modes
        self._attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT, HVACMode.AUTO]

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
    def hvac_mode(self) -> HVACMode:
        """Return current hvac mode."""
        if not self.coordinator.data:
            return HVACMode.HEAT
        # Program mode (UMD): manual vs schedule
        umd = str(self.coordinator.data.get("UMD", "")).lower()
        if umd in ["auto", "automatic", "program", "prog", "clock"]:
            return HVACMode.AUTO
        return HVACMode.HEAT

    @property
    def hvac_action(self) -> HVACAction:
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

    async def async_set_hvac_mode(self, hvac_mode: HVACMode | str) -> None:
        """Set new hvac mode."""
        _LOGGER.debug("Setting HVAC mode to %s", hvac_mode)
        # Normalize to HVACMode
        try:
            mode_enum = hvac_mode if isinstance(hvac_mode, HVACMode) else HVACMode(hvac_mode)
        except Exception:
            # Fallback: compare case-insensitively by value
            hv = str(hvac_mode).lower()
            mode_enum = HVACMode.HEAT if hv == "heat" else HVACMode.AUTO if hv == "auto" else HVACMode.OFF
        
        try:
            if mode_enum == HVACMode.OFF:
                await self.coordinator.async_set_mode("off")
            elif mode_enum == HVACMode.HEAT:
                await self.coordinator.async_set_mode("heat")
            elif mode_enum == HVACMode.AUTO:
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

# End of file