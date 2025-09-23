"""Config flow for Worcester Bosch Wave integration."""

import logging
import voluptuous as vol
from typing import Any, Dict, Optional

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_SERIAL_NUMBER,
    CONF_ACCESS_CODE,
    CONF_PASSWORD,
    ERROR_CANNOT_CONNECT,
    ERROR_INVALID_AUTH,
)
from .worcester_bosch_wave.status import WaveStatus

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_SERIAL_NUMBER): cv.string,
    vol.Required(CONF_ACCESS_CODE): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
})


class CannotConnect(Exception):
    pass


class InvalidAuth(Exception):
    pass


async def validate_input(hass: HomeAssistant, data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate the user input allows us to connect."""
    
    serial_number = data[CONF_SERIAL_NUMBER]
    access_code = data[CONF_ACCESS_CODE]
    password = data[CONF_PASSWORD]
    try:
        masked_access = access_code[:4] + "…" + access_code[-4:]
    except Exception:
        masked_access = "***"
    masked_pwd = "*" * len(password) if password else ""
    _LOGGER.debug(
        "Validating credentials serial=%s access=%s pwd_len=%d",
        serial_number,
        masked_access,
        len(password) if password else 0,
    )
    
    # Test the connection
    try:
        # Build and use the XMPP client entirely in an executor to avoid blocking the event loop
        def _sync_probe():
            client = WaveStatus(serial_number, access_code, password)
            client.update()
            return getattr(client, "data", None), getattr(client, "auth_failed", False)

        data_result, auth_failed = await hass.async_add_executor_job(_sync_probe)

        if not data_result:
            if auth_failed:
                raise InvalidAuth()
            raise CannotConnect()

        _LOGGER.info("Successfully validated Worcester Bosch Wave connection")

        # Return info that you want to store in the config entry
        return {
            "title": f"Worcester Bosch Wave ({serial_number})",
            CONF_SERIAL_NUMBER: serial_number,
            CONF_ACCESS_CODE: access_code,
            CONF_PASSWORD: password,
        }

    except InvalidAuth:
        raise
    except CannotConnect:
        raise
    except Exception as e:
        _LOGGER.error("Connection validation failed: %s", e)
        # Treat unexpected errors as connection issues for now
        raise CannotConnect()


class WorcesterWaveConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Worcester Bosch Wave."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", 
                data_schema=STEP_USER_DATA_SCHEMA,
                description_placeholders={
                    "serial_number": "Your thermostat serial number (e.g., 757940591)",
                    "access_code": "Your access code from the app (e.g., K5p4ietYG9DcJeDP)", 
                    "password": "Your user password (e.g., 3864)",
                }
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except InvalidAuth:
            _LOGGER.warning("Invalid credentials provided for Worcester Bosch Wave")
            errors["base"] = ERROR_INVALID_AUTH
        except CannotConnect:
            _LOGGER.exception("Cannot connect to Worcester Bosch Wave")
            errors["base"] = ERROR_CANNOT_CONNECT
        else:
            # Check if already configured
            await self.async_set_unique_id(user_input[CONF_SERIAL_NUMBER])
            self._abort_if_unique_id_configured()
            
            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", 
            data_schema=STEP_USER_DATA_SCHEMA, 
            errors=errors,
            description_placeholders={
                "serial_number": "Your thermostat serial number (e.g., 757940591)",
                "access_code": "Your access code from the app (e.g., K5p4ietYG9DcJeDP)", 
                "password": "Your user password (e.g., 3864)",
            }
        )
