import json

from messenger import WaveMessenger
from utils import parse_on_off


class WaveStatus(WaveMessenger):
    data = None

    current_switch_point = None
    current_temp = None
    is_boiler_on = None
    is_day_as_sunday = None
    is_holiday_mode = None
    is_hot_water_enabled = None
    is_temp_override_on = None
    is_tomorrow_as_sunday = None
    program_mode = None
    set_point = None
    temp_override_duration = None

    def __init__(self, serial_number, access_code, password):
        super().__init__(
            serial_number,
            access_code,
            password,
            'GET /ecus/rrc/uiStatus HTTP /1.0\nUser-Agent: NefitEasy',
        )

    def message(self, msg):
        """
        Process a message once it has been received
        """
        spl = str(msg['body']).split('\n\n')

        if len(spl) < 2:
            # Invalid message
            return
        else:
            to_decode = spl[1].strip()

            # Decode the encrypted message
            data = self.decode(to_decode)

            # For some reason we have a load of null characters at the end
            # of the message, so strip these out
            data = data.replace(b'\x00', b'')

            # 'decode' from bytes to str, with UTF-8 encoding
            # (a different sort of 'decode' to above!)
            data = data.decode('utf-8')
            if len(data) > 0:
                self.data = json.loads(data)['value']
                self.set_updated_values(self.data)
                self.disconnect()

    def set_updated_values(self, data):
        # Temperature set point (ie. temperature it is aiming for)
        self.set_point = float(data['TSP'])

        # Current thermostat temperature
        self.current_temp = float(data['IHT'])

        # Program mode: MANUAL or CLOCK
        self.program_mode = data['UMD']

        self.current_switch_point = float(data['CSP'])

        self.is_day_as_sunday = parse_on_off(data['DAS'])

        self.is_holiday_mode = parse_on_off(data['HMD'])

        self.is_hot_water_enabled = parse_on_off(data['DHW'])

        self.is_temp_override_on = parse_on_off(data['TOR'])

        self.is_tomorrow_as_sunday = parse_on_off(data['TAS'])

        self.temp_override_duration = float(data['TOD'])

        # Is the boiler on or off (ie. flame on or off)
        if data['BAI'] == 'No':
            self.is_boiler_on = False
        elif data['BAI'] == 'CH' or data['BAI'] == 'HW':
            self.is_boiler_on = True

    def update(self):
        self.run()
