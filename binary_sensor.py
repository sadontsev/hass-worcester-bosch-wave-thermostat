"""
Worcester Bosch Wave Binary Sensor Platform
Provides binary sensors for boolean metrics and status indicators.
"""

import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
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

# Binary sensor definitions
BINARY_SENSORS = [
    {
        "key": "PMR",
        "name": "Program Running",
        "entity_id": "program_running",
        "device_class": BinarySensorDeviceClass.RUNNING,
        "icon": "mdi:play-circle",
        "on_state": ["true", "on", "yes", "1"],
    },
    {
        "key": "BLE",
        "name": "Boiler Enabled",
        "entity_id": "boiler_enabled", 
        "device_class": BinarySensorDeviceClass.POWER,
        "icon": "mdi:fire",
        "on_state": ["true", "on", "yes", "1"],
    },
    {
        "key": "BBE",
        "name": "Backup Boiler Enabled",
        "entity_id": "backup_boiler_enabled",
        "device_class": BinarySensorDeviceClass.POWER,
        "icon": "mdi:fire-alert",
        "on_state": ["true", "on", "yes", "1"],
    },
    {
        "key": "BMR",
        "name": "Boiler Maintenance Required",
        "entity_id": "maintenance_required",
        "device_class": BinarySensorDeviceClass.PROBLEM,
        "icon": "mdi:wrench-clock",
        "on_state": ["true", "on", "yes", "1"],
    },
    {
        "key": "DHW",
        "name": "Hot Water Demand",
        "entity_id": "hot_water_demand",
        "device_class": BinarySensorDeviceClass.HEAT,
        "icon": "mdi:water-thermometer",
        "on_state": ["on", "active", "yes", "1"],
    },
    {
        "key": "HED_EN",
        "name": "Holiday Mode Enabled",
        "entity_id": "holiday_mode",
        "icon": "mdi:airplane",
        "on_state": ["true", "on", "yes", "1"],
    },
    {
        "key": "HED_DEV",
        "name": "Holiday Mode Device",
        "entity_id": "holiday_device",
        "icon": "mdi:airplane-cog",
        "on_state": ["true", "on", "yes", "1"],
    },
    {
        "key": "FAH",
        "name": "First Aid Help",
        "entity_id": "first_aid_help",
        "device_class": BinarySensorDeviceClass.PROBLEM,
        "icon": "mdi:medical-bag",
        "on_state": ["true", "on", "yes", "1"],
    },
    {
        "key": "DOT",
        "name": "System Override Active",
        "entity_id": "override_active",
        "icon": "mdi:hand-back-right",
        "on_state": ["true", "on", "yes", "1"],
    },
]

# Special handling for BAI (Boiler Active Indicator)
BAI_BINARY_SENSOR = {
    "key": "BAI",
    "name": "Boiler Active",
    "entity_id": "boiler_active",
    "device_class": BinarySensorDeviceClass.HEAT,
    "icon": "mdi:fire",
    "on_state": ["true", "on", "yes", "1", "active"],
    "off_state": ["false", "off", "no", "0", "inactive"],
}

ALL_BINARY_SENSORS = BINARY_SENSORS + [BAI_BINARY_SENSOR]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Worcester Bosch Wave binary sensor platform."""
    
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    
    binary_sensors = []
    for sensor_config in ALL_BINARY_SENSORS:
        binary_sensors.append(
            WorcesterWaveBinarySensor(
                coordinator,
                config_entry,
                sensor_config,
            )
        )
    
    async_add_entities(binary_sensors)


class WorcesterWaveBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Worcester Bosch Wave binary sensor."""

    def __init__(
        self,
        coordinator: WorcesterWaveDataUpdateCoordinator,
        config_entry: ConfigEntry,
        sensor_config: dict[str, Any],
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        
        self._config = sensor_config
        self._data_key = sensor_config["key"]
        self._serial_number = config_entry.data[CONF_SERIAL_NUMBER]
        
        # Entity properties
        self._attr_name = f"Worcester Wave {sensor_config['name']}"
        self._attr_unique_id = f"{DOMAIN}_{self._serial_number}_{sensor_config['entity_id']}"
        
        # Device class and icon
        if "device_class" in sensor_config:
            self._attr_device_class = sensor_config["device_class"]
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
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        if not self.coordinator.data:
            return None
            
        raw_value = self.coordinator.data.get(self._data_key)
        
        if raw_value is None:
            return None
            
        # Convert to string and normalize
        str_value = str(raw_value).lower().strip()
        
        # Check explicit on states
        on_states = self._config.get("on_state", ["true", "on", "yes", "1"])
        if str_value in [state.lower() for state in on_states]:
            return True
            
        # Check explicit off states if defined
        off_states = self._config.get("off_state", ["false", "off", "no", "0"])
        if str_value in [state.lower() for state in off_states]:
            return False
            
        # Handle special cases
        if self._data_key == "BAI":
            # BAI can be "No" (off) or other values (on)
            return str_value not in ["no", "false", "off", "0", "inactive"]
        elif self._data_key == "DHW":
            # DHW status can be "on"/"off" or similar
            return str_value in ["on", "active", "true", "yes", "1"]
            
        # Default: try to parse as boolean
        try:
            return bool(int(str_value))
        except ValueError:
            # If it's not a number, check if it's a boolean-like string
            return str_value in ["true", "on", "yes", "active", "enabled"]

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
        
        # Add sensor type
        if self._data_key in ["PMR", "BLE", "BBE", "BAI"]:
            attrs["category"] = "boiler_status"
        elif self._data_key in ["BMR", "FAH"]:
            attrs["category"] = "maintenance"
        elif self._data_key in ["DHW"]:
            attrs["category"] = "hot_water"
        elif self._data_key in ["HED_EN", "HED_DEV"]:
            attrs["category"] = "holiday_mode"
        elif self._data_key in ["DOT"]:
            attrs["category"] = "override"
        else:
            attrs["category"] = "system"
            
        return attrs