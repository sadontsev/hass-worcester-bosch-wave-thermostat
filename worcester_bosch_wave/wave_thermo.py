from .set import WaveSet
from .status import WaveStatus

from .constants import (
    CLOCK,
    MANUAL,
    OFF,
    ON,
    PATH_BASE,
)


class WaveThermostat:
    def __init__(self, serial_number, access_code, password):
        self.status = WaveStatus(
            serial_number=serial_number, access_code=access_code, password=password
        )

        self.setter = WaveSet(
            serial_number=serial_number, access_code=access_code, password=password
        )

    def set_base_mode(self, mode):
        """
        Set the base control mode of the thermostat (when not overridden)

        mode: Control mode, either MANUAL or CLOCK
        """
        self.setter.post_message(f'{PATH_BASE}usermode', mode)

    def set_temperature(self, temperature):
        """
        Set the temperature to the float provided

        :param temperature: Desired temperature in degrees celsius, 0.5c increments
        """
        self.status.update()

        if self.status.program_mode == MANUAL:
            self.setter.post_message(f'{PATH_BASE}temperatureRoomManual', temperature)
        else:
            self.setter.post_message(
                f'{PATH_BASE}manualTempOverride/temperature', temperature
            )
            self.override(should_override=True)

    def override(self, should_override):
        if should_override:
            self.setter.post_message(f'{PATH_BASE}manualTempOverride/status', ON)
        else:
            self.setter.post_message(f'{PATH_BASE}manualTempOverride/status', OFF)
