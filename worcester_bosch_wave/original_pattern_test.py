#!/usr/bin/env python3
"""
Worcester Bosch Wave - Original Pattern Implementation
Based on the proven working pywavethermo repository
"""

import os
import base64
import json
import hashlib
import time
from Crypto.Cipher import AES
import slixmpp

# Load environment variables from .env file
def load_env_file():
    """Load environment variables from .env file"""
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value.strip('"\'')
        return True
    return False

def get_md5(data):
    """Get MD5 hash of data"""
    m = hashlib.md5()
    m.update(data)
    return m.digest()

def parse_on_off(s):
    """Parse on/off strings to boolean"""
    return s == 'on'

class BaseWaveMessageBot(slixmpp.ClientXMPP):
    secret = b'X\xf1\x8dp\xf6g\xc9\xc7\x9e\xf7\xdeC[\xf0\xf9\xb1U;\xbbna\x81b\x12\xab\x80\xe5\xb0\xd3Q\xfb\xb1'

    def __init__(self, serial_number, access_code, password, message):
        jid = f"rrccontact_{serial_number}@wa2-mz36-qrmzh6.bosch.de"
        connection_password = f"Ct7ZR03b_{access_code}"

        slixmpp.ClientXMPP.__init__(self, jid, connection_password)

        # Critical: Disable TLS as per 2018 fix
        self.use_tls = False

        self.recipient = f"rrcgateway_{serial_number}@wa2-mz36-qrmzh6.bosch.de"
        self.msg = message

        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.message)

        self.connected = False

        abyte1 = get_md5(access_code.encode() + self.secret)
        abyte2 = get_md5(self.secret + password.encode())

        self.key = abyte1 + abyte2

    def connect(self):
        self.connected = True
        # Use the exact same connection parameters as the working original
        return slixmpp.ClientXMPP.connect(self, ('wa2-mz36-qrmzh6.bosch.de', 5222))

    def disconnect(self):
        self.connected = False
        return slixmpp.ClientXMPP.disconnect(self)

    def run(self):
        print("🔌 Connecting to Worcester Bosch...")
        self.connect()
        print("📤 Sending message immediately...")
        self.go()
        print("📡 Processing XMPP events...")
        
        # Try to mimic the original blocking behavior
        try:
            # Start the event loop - this should trigger session_start
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Wait for a short time to allow processing
            for i in range(20):
                time.sleep(0.5)
                print(f"⏱️ Processing {i+1}/20...")
                if not self.connected:
                    break
                    
        except Exception as e:
            print(f"❌ Processing error: {e}")

    def start(self, event):
        print("🚀 Session started!")
        self.send_presence()
        self.get_roster()

    def go(self):
        print(f"📤 Sending to {self.recipient}")
        print(f"📝 Message: {self.msg[:50]}...")
        
        if not self.connected:
            print("🔌 Not connected, connecting...")
            self.connect()

        self.send_message(mto=self.recipient, mbody=self.msg, mtype='chat')
        print("✅ Message sent!")

    def set_message(self, url, value):
        j = '{"value":%s}' % (repr(value))
        remainder = len(j) % 16
        j = j + '\x00' * (16 - remainder)
        
        self.msg = f"PUT {url} HTTP:/1.0\nContent-Type: application/json\nContent-Length: 25\nUser-Agent: NefitEasy\n\n\n\n{self.encode(j).decode('utf-8')}\n"

    def encode(self, s):
        a = AES.new(self.key, AES.MODE_ECB)
        if isinstance(s, str):
            s = s.encode('utf-8')
        res = a.encrypt(s)
        return base64.b64encode(res)

    def decode(self, data):
        decoded = base64.b64decode(data)
        a = AES.new(self.key, AES.MODE_ECB)
        return a.decrypt(decoded)

class StatusBot(BaseWaveMessageBot):
    current_temp = None
    set_point = None
    boiler_on = None
    data = None

    def __init__(self, serial_number, access_code, password):
        super().__init__(serial_number, access_code, password, 
                        "GET /ecus/rrc/uiStatus HTTP /1.0\nUser-Agent: NefitEasy")

    def message(self, msg):
        """Process a message once it has been received"""
        print(f"📨 Received message from {msg['from']}")
        print(f"📝 Message body: {msg['body']}")
        
        spl = str(msg['body']).split("\n\n")
        print(f"🔍 Split into {len(spl)} parts")

        if len(spl) < 2:
            print("❌ Invalid message - less than 2 parts")
            return
        else:
            to_decode = spl[1].strip()
            print(f"🔐 Decoding: {to_decode[:50]}...")

            try:
                # Decode the encrypted message
                data = self.decode(to_decode)
                print(f"🔓 Decoded bytes: {len(data)} bytes")

                # Strip null characters
                data = data.replace(b'\x00', b'')

                # Decode to string
                data = data.decode('utf-8')
                print(f"📄 UTF-8 decoded: {data[:100]}...")
                
                if len(data) > 0:
                    json_data = json.loads(data)
                    self.data = json_data['value']
                    print(f"✅ Successfully parsed JSON data!")
                    
                    # Parse the temperature data
                    self.set_point = float(self.data['TSP'])
                    self.current_temp = float(self.data['IHT'])
                    
                    print(f"🌡️ Current temp: {self.current_temp}°C")
                    print(f"🎯 Set point: {self.set_point}°C")
                    
                    self.disconnect()
                    
            except Exception as e:
                print(f"❌ Decode error: {e}")
                import traceback
                traceback.print_exc()

    def update(self):
        self.run()

def test_original_pattern():
    """Test using the exact original working pattern"""
    load_env_file()
    
    serial_number = os.environ.get('WAVE_SERIAL_NUMBER', '').replace(' ', '').strip('"')
    access_code = os.environ.get('WAVE_ACCESS_CODE', '').replace(' ', '').strip('"')
    password = os.environ.get('WAVE_PASSWORD', '').strip('"')
    
    print("🔬 Worcester Bosch Wave - Original Pattern Test")
    print("=" * 60)
    print(f"📋 Serial: {serial_number}")
    print(f"📋 Access: {access_code}")
    print(f"📋 Password: {'*' * len(password)}")
    
    print("\n🔍 Testing status update...")
    status = StatusBot(serial_number, access_code, password)
    status.update()
    
    if status.data:
        print("\n🎉 SUCCESS! Worcester Bosch Wave is working!")
        print(f"Current temperature: {status.current_temp}°C")
        print(f"Set point: {status.set_point}°C")
        print("Full data available - thermostat is responsive!")
        return True
    else:
        print("\n❌ No data received")
        return False

if __name__ == "__main__":
    success = test_original_pattern()
    exit(0 if success else 1)