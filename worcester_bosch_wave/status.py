import json

from .messenger import WaveMessenger
from .utils import parse_on_off


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
        print(f"📨 Received message: {msg}")
        print(f"📝 Message body: {msg['body'][:200]}...")
        
        spl = str(msg['body']).split('\n\n')
        print(f"🔍 Split parts: {len(spl)} parts")
        
        if len(spl) < 2:
            # Invalid message
            print("❌ Invalid message - less than 2 parts")
            return
        else:
            to_decode = spl[1].strip()
            print(f"🔐 To decode: {len(to_decode)} characters")

            # Decode the encrypted message
            try:
                data = self.decode(to_decode)
                print(f"🔓 Decoded bytes: {len(data)} bytes")

                # For some reason we have a load of null characters at the end
                # of the message, so strip these out
                data = data.replace(b'\x00', b'')
                print(f"🧹 After null removal: {len(data)} bytes")

                # 'decode' from bytes to str, with UTF-8 encoding
                # (a different sort of 'decode' to above!)
                data = data.decode('utf-8')
                print(f"📄 UTF-8 decoded: {len(data)} characters")
                
                if len(data) > 0:
                    json_data = json.loads(data)
                    print(f"📋 JSON parsed successfully")
                    
                    self.data = json_data['value']
                    print(f"✅ Final data extracted")
                    self.set_updated_values(self.data)
                    
                    # Mark that we received a response
                    self.response_received = True
                    
                    self.disconnect()
                else:
                    print("❌ Empty data after decoding")
            except Exception as e:
                print(f"❌ Decoding error: {e}")
                import traceback
                traceback.print_exc()

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
