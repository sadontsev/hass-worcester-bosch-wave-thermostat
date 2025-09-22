#!/usr/bin/env python3
"""
Worcester Bosch Wave XMPP Authentication Test
Focus only on establishing authenticated session
"""

import os
import time
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

load_env_file()

class AuthTestClient(slixmpp.ClientXMPP):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        
        # Disable SSL/TLS as per 2018 fix
        self.use_tls = False
        
        self.connected = False
        self.authenticated = False
        self.session_started = False
        
        self.add_event_handler("connected", self.on_connected)
        self.add_event_handler("session_start", self.on_session_start)
        self.add_event_handler("failed_auth", self.on_auth_failed)
        self.add_event_handler("disconnected", self.on_disconnected)
        
    def on_connected(self, event):
        print(f"✅ XMPP Connected: {event}")
        self.connected = True
        
    def on_session_start(self, event):
        print(f"🚀 XMPP Session Started: {event}")
        self.session_started = True
        self.send_presence()
        self.get_roster()
        
    def on_auth_failed(self, event):
        print(f"❌ Authentication Failed: {event}")
        self.authenticated = False
        
    def on_disconnected(self, event):
        print(f"🔌 Disconnected: {event}")
        
def test_authentication():
    """Test XMPP authentication with Worcester Bosch credentials"""
    
    serial_number = os.environ.get('WAVE_SERIAL_NUMBER', '').replace(' ', '')
    access_code = os.environ.get('WAVE_ACCESS_CODE', '').replace(' ', '')
    password = os.environ.get('WAVE_PASSWORD', '')
    
    print("🔐 Worcester Bosch Wave Authentication Test")
    print("=" * 50)
    print(f"Serial: {serial_number}")
    print(f"Access: {access_code}")
    print(f"Password: {'*' * len(password)}")
    
    # Create JID and password as per protocol
    jid = f'rrccontact_{serial_number}@wa2-mz36-qrmzh6.bosch.de'
    xmpp_password = f'Ct7ZR03b_{access_code}'
    
    print(f"\n📧 JID: {jid}")
    print(f"🔑 XMPP Password: {xmpp_password}")
    
    # Create client
    client = AuthTestClient(jid, xmpp_password)
    
    print(f"\n🔌 Connecting to wa2-mz36-qrmzh6.bosch.de:5222...")
    
    if client.connect(('wa2-mz36-qrmzh6.bosch.de', 5222)):
        print("✅ Connection initiated")
        
        # Wait for authentication
        for i in range(15):
            time.sleep(1)
            print(f"⏱️ {i+1}/15 - Connected: {client.connected}, Session: {client.session_started}")
            
            if client.session_started:
                print("🎉 SUCCESS! XMPP session established!")
                client.disconnect()
                return True
                
            if not client.connected:
                print("❌ Connection lost")
                break
                
        print("⏱️ Timeout - authentication failed")
        client.disconnect()
        
    else:
        print("❌ Connection failed")
        
    return False

if __name__ == "__main__":
    success = test_authentication()
    if success:
        print("\n✅ Authentication test PASSED")
        print("The Worcester Bosch Wave thermostat is responding!")
    else:
        print("\n❌ Authentication test FAILED")
        print("Check credentials or Worcester Bosch may have changed their system")