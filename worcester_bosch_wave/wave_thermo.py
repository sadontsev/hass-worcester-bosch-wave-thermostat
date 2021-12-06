from set import WaveSet
from status import WaveStatus

from worcester_bosch_wave.constants import PATH_BASE


class WaveThermostat:
    def __init__(self, serial_number, access_code, password):
        self.status = WaveStatus(
            serial_number=serial_number, access_code=access_code, password=password
        )

        self.setter = WaveSet(
            serial_number=serial_number, access_code=access_code, password=password
        )

    def set_mode(self, mode):
        """
        Set the control mode of the thermostat

        mode: Control mode, either "manual" or "clock"
        """
        self.setter.post_message(f'{PATH_BASE}usermode', mode)

    def set_temperature(self, temperature):
        self.status.update()

        if self.status.program_mode == 'manual':
            self.setter.post_message(f'{PATH_BASE}temperatureRoomManual', temperature)
        else:
            self.setter.post_message(
                f'{PATH_BASE}manualTempOverride/temperature', temperature
            )
            self.setter.post_message(f'{PATH_BASE}manualTempOverride/status', 'on')

    def override(self, should_override):
        if should_override:
            self.setter.post_message(f'{PATH_BASE}manualTempOverride/status', 'on')
        else:
            self.setter.post_message(f'{PATH_BASE}manualTempOverride/status', 'off')
