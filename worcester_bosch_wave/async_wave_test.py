#!/usr/bin/env python3
"""
Worcester Bosch Wave - Async Implementation for slixmpp
Properly adapted from the original working pattern
"""

import os
import base64
import json
import hashlib
import asyncio
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

class WorcesterWaveClient(slixmpp.ClientXMPP):
    def __init__(self, serial_number, access_code, password):
        # Clean inputs
        serial_number = serial_number.replace(' ', '').strip('"')
        access_code = access_code.replace(' ', '').strip('"')
        password = password.strip('"')
        
        # Create JID and XMPP password
        jid = f"rrccontact_{serial_number}@wa2-mz36-qrmzh6.bosch.de"
        xmpp_password = f"Ct7ZR03b_{access_code}"
        
        super().__init__(jid, xmpp_password)
        
        # Disable TLS as per 2018 fix
        self.use_tls = False
        
        # Store connection details
        self.recipient = f"rrcgateway_{serial_number}@wa2-mz36-qrmzh6.bosch.de"
        self.serial_number = serial_number
        self.access_code = access_code
        self.user_password = password
        
        # Create encryption key
        secret = b'X\xf1\x8dp\xf6g\xc9\xc7\x9e\xf7\xdeC[\xf0\xf9\xb1U;\xbbna\x81b\x12\xab\x80\xe5\xb0\xd3Q\xfb\xb1'
        abyte1 = get_md5(access_code.encode() + secret)
        abyte2 = get_md5(secret + password.encode())
        self.key = abyte1 + abyte2
        
        # Result storage
        self.thermostat_data = None
        self.current_temp = None
        self.set_point = None
        self.success = False
        
        # Event handlers
        self.add_event_handler("session_start", self.on_session_start)
        self.add_event_handler("message", self.on_message)
        self.add_event_handler("disconnected", self.on_disconnected)
        
        print(f"🔐 JID: {jid}")
        print(f"🔑 Password: {xmpp_password}")
        print(f"📡 Recipient: {self.recipient}")
        print(f"🔐 Encryption key: {len(self.key)} bytes")
    
    async def on_session_start(self, event):
        """Called when XMPP session starts"""
        print("🚀 XMPP session started!")
        self.send_presence()
        await self.get_roster()
        
        # Send status request immediately as per original pattern
        await self.request_status()
    
    async def request_status(self):
        """Request thermostat status"""
        message_body = "GET /ecus/rrc/uiStatus HTTP /1.0\nUser-Agent: NefitEasy"
        
        print(f"📤 Sending status request to {self.recipient}")
        print(f"📝 Message: {message_body}")
        
        self.send_message(
            mto=self.recipient,
            mbody=message_body,
            mtype='chat'
        )
        print("✅ Status request sent!")
    
    def on_message(self, msg):
        """Handle incoming messages from thermostat"""
        print(f"📨 Received message from: {msg['from']}")
        print(f"📝 Raw message: {msg['body']}")
        
        try:
            # Parse the response as per original pattern
            spl = str(msg['body']).split("\n\n")
            print(f"🔍 Message split into {len(spl)} parts")
            
            if len(spl) < 2:
                print("❌ Invalid message format")
                return
            
            # Get the encrypted data part
            to_decode = spl[1].strip()
            print(f"🔐 Encrypted data: {to_decode[:50]}...")
            
            # Decode using AES
            decoded_bytes = self.decode_aes(to_decode)
            print(f"🔓 Decoded {len(decoded_bytes)} bytes")
            
            # Remove null padding
            cleaned_data = decoded_bytes.replace(b'\x00', b'')
            
            # Convert to string
            json_string = cleaned_data.decode('utf-8')
            print(f"📄 JSON string: {json_string[:100]}...")
            
            # Parse JSON
            if len(json_string) > 0:
                json_data = json.loads(json_string)
                self.thermostat_data = json_data['value']
                
                # Extract temperature data
                self.current_temp = float(self.thermostat_data['IHT'])
                self.set_point = float(self.thermostat_data['TSP'])
                
                print(f"🎉 SUCCESS! Thermostat data received!")
                print(f"🌡️ Current temperature: {self.current_temp}°C")
                print(f"🎯 Set point: {self.set_point}°C")
                
                self.success = True
                
                # Disconnect after successful response
                self.disconnect()
            else:
                print("❌ Empty response data")
                
        except Exception as e:
            print(f"❌ Error processing message: {e}")
            import traceback
            traceback.print_exc()
    
    def decode_aes(self, data):
        """Decode AES encrypted data"""
        decoded = base64.b64decode(data)
        cipher = AES.new(self.key, AES.MODE_ECB)
        return cipher.decrypt(decoded)
    
    def on_disconnected(self, event):
        """Called when disconnected"""
        print(f"🔌 Disconnected: {event}")

async def test_worcester_wave():
    """Test Worcester Bosch Wave connection with proper async handling"""
    load_env_file()
    
    serial_number = os.environ.get('WAVE_SERIAL_NUMBER', '')
    access_code = os.environ.get('WAVE_ACCESS_CODE', '')
    password = os.environ.get('WAVE_PASSWORD', '')
    
    print("🔬 Worcester Bosch Wave - Async Test")
    print("=" * 50)
    
    if not all([serial_number, access_code, password]):
        print("❌ Missing credentials")
        return False
    
    # Create client
    client = WorcesterWaveClient(serial_number, access_code, password)
    
    print("\n🔌 Connecting to Worcester Bosch server...")
    
    # Connect with proper async handling
    client.connect(('wa2-mz36-qrmzh6.bosch.de', 5222))
    
    # Wait for response with timeout
    timeout = 30
    for i in range(timeout):
        await asyncio.sleep(1)
        print(f"⏱️ Waiting {i+1}/{timeout}s...")
        
        if client.success:
            print("\n✅ SUCCESS! Worcester Bosch Wave is working!")
            return True
        
        if not client.is_connected():
            print("❌ Connection lost")
            break
    
    print(f"\n⏱️ Timeout after {timeout} seconds")
    client.disconnect()
    return False

def main():
    """Main async wrapper"""
    try:
        success = asyncio.run(test_worcester_wave())
        if success:
            print("\n🎉 Worcester Bosch Wave test PASSED!")
            print("The thermostat is accessible and responding!")
        else:
            print("\n❌ Worcester Bosch Wave test FAILED!")
        return success
    except Exception as e:
        print(f"❌ Async error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)