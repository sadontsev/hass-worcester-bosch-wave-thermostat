"""
Worcester Bosch Wave Sensor Platform
Provides comprehensive sensor data organized into logical groups.
"""

import logging
from typing import Any, Dict

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfTemperature,
    UnitOfTime,
    PERCENTAGE,
)
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

# Sensor definitions organized by category
TEMPERATURE_SENSORS = [
    {
        "key": "IHT",
        "name": "Current Temperature", 
        "entity_id": "current_temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit": UnitOfTemperature.CELSIUS,
        "icon": "mdi:thermometer",
    },
    {
        "key": "TSP",
        "name": "Target Temperature",
        "entity_id": "target_temperature", 
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit": UnitOfTemperature.CELSIUS,
        "icon": "mdi:target",
    },
    {
        "key": "MMT",
        "name": "Manual Mode Temperature",
        "entity_id": "manual_temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "icon": "mdi:thermometer-lines",
    },
    {
        "key": "CSP",
        "name": "Current Switch Point",
        "entity_id": "switch_point",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "icon": "mdi:thermometer-auto",
    },
    {
        "key": "TOT",
        "name": "Schedule Temperature",
        "entity_id": "schedule_temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "icon": "mdi:calendar-clock",
    },
]

CONTROL_SENSORS = [
    {
        "key": "UMD",
        "name": "Program Mode",
        "entity_id": "program_mode",
        "icon": "mdi:cog-outline",
    },
    {
        "key": "CPM",
        "name": "Control Mode",
        "entity_id": "control_mode", 
        "icon": "mdi:auto-mode",
    },
    {
        "key": "BAI",
        "name": "Boiler Status",
        "entity_id": "boiler_status",
        "icon": "mdi:fire",
    },
    {
        "key": "IHS",
        "name": "System Health",
        "entity_id": "system_health",
        "icon": "mdi:heart-pulse",
    },
]

TIME_SENSORS = [
    {
        "key": "TOD",
        "name": "Override Duration",
        "entity_id": "override_duration",
        "device_class": SensorDeviceClass.DURATION,
        "unit": UnitOfTime.HOURS,
        "icon": "mdi:timer-outline",
    },
    {
        "key": "CTD",
        "name": "System Time",
        "entity_id": "system_time",
        "device_class": SensorDeviceClass.TIMESTAMP,
        "icon": "mdi:clock-outline",
    },
    {
        "key": "CTR",
        "name": "Current Time Remaining",
        "entity_id": "time_remaining",
        "icon": "mdi:timer",
    },
]

DIAGNOSTIC_SENSORS = [
    {
        "key": "ARS",
        "name": "Schedule Point ARS",
        "entity_id": "schedule_ars",
        "icon": "mdi:calendar-text",
    },
    {
        "key": "PMR",
        "name": "Program Remaining",
        "entity_id": "program_remaining",
        "icon": "mdi:progress-clock",
    },
    {
        "key": "RS",
        "name": "Reset Status",
        "entity_id": "reset_status",
        "icon": "mdi:restart",
    },
    {
        "key": "FPA",
        "name": "Frost Protection Active",
        "entity_id": "frost_protection",
        "icon": "mdi:snowflake",
    },
    {
        "key": "ESI",
        "name": "Energy Saving Indicator",
        "entity_id": "energy_saving",
        "icon": "mdi:leaf",
    },
]

ALL_SENSORS = TEMPERATURE_SENSORS + CONTROL_SENSORS + TIME_SENSORS + DIAGNOSTIC_SENSORS


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Worcester Bosch Wave sensor platform."""
    
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    
    sensors = []
    for sensor_config in ALL_SENSORS:
        sensors.append(
            WorcesterWaveSensor(
                coordinator,
                config_entry,
                sensor_config,
            )
        )
    
    async_add_entities(sensors)


class WorcesterWaveSensor(CoordinatorEntity, SensorEntity):
    """Worcester Bosch Wave sensor."""

    def __init__(
        self,
        coordinator: WorcesterWaveDataUpdateCoordinator,
        config_entry: ConfigEntry,
        sensor_config: Dict[str, Any],
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        
        self._config = sensor_config
        self._data_key = sensor_config["key"]
        self._serial_number = config_entry.data[CONF_SERIAL_NUMBER]
        
        # Entity properties
        self._attr_name = f"Worcester Wave {sensor_config['name']}"
        self._attr_unique_id = f"{DOMAIN}_{self._serial_number}_{sensor_config['entity_id']}"
        
        # Device class and units
        if "device_class" in sensor_config:
            self._attr_device_class = sensor_config["device_class"]
        if "state_class" in sensor_config:
            self._attr_state_class = sensor_config["state_class"]
        if "unit" in sensor_config:
            self._attr_native_unit_of_measurement = sensor_config["unit"]
        if "icon" in sensor_config:
            self._attr_icon = sensor_config["icon"]

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
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
            
        raw_value = self.coordinator.data.get(self._data_key)
        
        if raw_value is None:
            return None
            
        # Handle temperature values
        if self._data_key in ["IHT", "TSP", "MMT", "CSP", "TOT"]:
            try:
                return float(raw_value)
            except (ValueError, TypeError):
                return None
                
        # Handle duration values  
        elif self._data_key == "TOD":
            try:
                return float(raw_value)
            except (ValueError, TypeError):
                return None
                
        # Handle timestamp values
        elif self._data_key == "CTD":
            # Parse timestamp format: "2025-09-22T18:33:30+01:00 Mo"
            if isinstance(raw_value, str):
                try:
                    # Extract ISO-8601 portion before any trailing token like weekday
                    iso_part = raw_value.split(" ")[0]
                    from datetime import datetime
                    # datetime.fromisoformat supports offsets like +01:00
                    dt = datetime.fromisoformat(iso_part)
                    return dt
                except Exception:
                    return None
            return None
            
        # Handle boolean-like values
        elif self._data_key in ["PMR", "BLE", "BBE", "BMR", "HED_EN", "HED_DEV", "FAH", "DOT"]:
            if isinstance(raw_value, str):
                return raw_value.lower() in ["true", "on", "yes", "1"]
            return bool(raw_value)
            
        # Return raw value for everything else
        return raw_value

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return {}
            
        attrs = {
            "data_key": self._data_key,
            "raw_value": self.coordinator.data.get(self._data_key),
            "last_update": self.coordinator.data.get("CTD"),
        }
        
        # Add category-specific attributes
        if self._data_key in [sensor["key"] for sensor in TEMPERATURE_SENSORS]:
            attrs["category"] = "temperature"
        elif self._data_key in [sensor["key"] for sensor in CONTROL_SENSORS]:
            attrs["category"] = "control"
        elif self._data_key in [sensor["key"] for sensor in TIME_SENSORS]:
            attrs["category"] = "time"
        else:
            attrs["category"] = "diagnostic"
            
        return attrs