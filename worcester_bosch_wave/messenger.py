import base64
import asyncio
import slixmpp
from Crypto.Cipher import AES
from .utils import get_md5

from .constants import SECRET


class WaveMessenger(slixmpp.ClientXMPP):
    def __init__(self, serial_number, access_code, password, message):

        # Clean serial number and access code of any spaces to ensure valid XMPP JID
        serial_number = serial_number.replace(' ', '').strip('"')
        access_code = access_code.replace(' ', '').strip('"')
        password = password.strip('"')

        jid = f'rrccontact_{serial_number}@wa2-mz36-qrmzh6.bosch.de'
        connection_password = f'Ct7ZR03b_{access_code}'

        slixmpp.ClientXMPP.__init__(self, jid, connection_password)

        self.recipient = f'rrcgateway_{serial_number}@wa2-mz36-qrmzh6.bosch.de'
        self.msg = message

        # Configure for Worcester Bosch Wave protocol - disable SSL/TLS as per 2018 fix
        self.use_tls = False  # Disable TLS - Bosch turned off SSL/TLS in 2018
        self.auto_reconnect = False

        self.add_event_handler('session_start', self.start)
        self.add_event_handler('message', self.message)
        self.add_event_handler('connected', self.on_connected)
        self.add_event_handler('disconnected', self.on_disconnected)
        self.add_event_handler('failed_auth', self.on_failed_auth)
        self.add_event_handler('stream_error', self.on_stream_error)

        self.connected = False
        self.session_started = False
        self.message_sent = False
        self.response_received = False

        # Use cleaned access code for key generation
        abyte_1 = get_md5(access_code.encode() + SECRET)
        abyte_2 = get_md5(SECRET + password.encode())

        self.key = abyte_1 + abyte_2

    def on_connected(self, event):
        print(f"🔗 XMPP connected: {event}")
        self.connected = True

    def on_disconnected(self, event):
        print(f"🔌 XMPP disconnected: {event}")
        self.connected = False

    def on_failed_auth(self, event):
        print(f"❌ XMPP authentication failed: {event}")
        self.connected = False

    def on_stream_error(self, event):
        print(f"⚠️ XMPP stream error: {event}")

    def connect(self, **kwargs):
        self.connected = True
        # Connect with SSL/TLS explicitly disabled (2018 Bosch change)
        return slixmpp.ClientXMPP.connect(
            self, ('wa2-mz36-qrmzh6.bosch.de', 5222)
        )

    def disconnect(self, **kwargs):
        self.connected = False
        return slixmpp.ClientXMPP.disconnect(self)

    def run(self):
        """Run the XMPP client with proper async handling"""
        return asyncio.run(self._async_run())

    async def _async_run(self):
        """Async implementation of the XMPP client"""
        print(f"🔌 Connecting to wa2-mz36-qrmzh6.bosch.de:5222...")
        self.connect(('wa2-mz36-qrmzh6.bosch.de', 5222))

        # Wait for response with timeout
        timeout = 15
        for i in range(timeout):
            await asyncio.sleep(1)

            if self.response_received:
                print("✅ Response received successfully!")
                return True

            if not self.is_connected():
                print("❌ Connection lost")
                break

        print("⏱️ Timeout waiting for response")
        if self.is_connected():
            self.disconnect()
        return False

    async def start(self, event):
        """Handle session start event"""
        print("🚀 XMPP session started")
        self.session_started = True
        self.send_presence()
        await self.get_roster()

        # Send the message immediately after session establishment
        await self.go()

    async def go(self):
        """Send the message"""
        print(f"📤 Sending message to {self.recipient}")
        print(f"📝 Message content: {self.msg[:100]}...")

        self.send_message(mto=self.recipient, mbody=self.msg, mtype='chat')
        self.message_sent = True
        print("✅ Message sent, waiting for response...")

    def set_message(self, url, value):
        j = '{"value":%s}' % (repr(value))

        remainder = len(j) % 16

        j = j + '\x00' * (16 - remainder)

        self.msg = (
            'PUT {} HTTP:/1.0\n'
            'Content-Type: application/json\n'
            'Content-Length: 25\n'
            'User-Agent: NefitEasy\n'
            '\n\n\n{}\n'
        ).format(url, self.encode(j).decode('utf-8'))

    def encode(self, s):
        a = AES.new(self.key, AES.MODE_ECB)
        # Ensure s is bytes for encryption
        if isinstance(s, str):
            s = s.encode('utf-8')
        res = a.encrypt(s)
        return base64.b64encode(res)

    def decode(self, data):
        decoded = base64.b64decode(data)
        a = AES.new(self.key, AES.MODE_ECB)
        return a.decrypt(decoded)

    def run(self):
        print("🔌 Starting XMPP connection...")
        success = self.connect()
        print(f"� Connect result: {success}")

        if success:
            print("📡 Processing XMPP events...")
            import time
            # Give time for connection, authentication, and message exchange
            for i in range(10):
                time.sleep(1)
                print(f"⏱️ Waiting {i+1}/10 - Connected: {self.connected}, Session: {self.session_started}")
                if self.session_started and self.message_sent:
                    break
            print("🏁 XMPP processing completed")
        else:
            print("❌ XMPP connection failed")

    def start(self, event):
        print("🚀 XMPP session started")
        self.send_presence()
        self.get_roster()
        self.session_started = True
        # Send the message after the session is established
        self.go()

    def go(self):
        if not self.session_started:
            print("⚠️ Session not started yet, cannot send message")
            return

        print(f"📤 Sending message to {self.recipient}")
        print(f"📝 Message content: {self.msg[:100]}...")
        self.send_message(mto=self.recipient, mbody=self.msg, mtype='chat')
        self.message_sent = True
        print("✅ Message sent, waiting for response...")

    def set_message(self, url, value):
        j = '{"value":%s}' % (repr(value))

        remainder = len(j) % 16

        j = j + '\x00' * (16 - remainder)

        self.msg = (
            'PUT {} HTTP:/1.0\n'
            'Content-Type: application/json\n'
            'Content-Length: 25\n'
            'User-Agent: NefitEasy\n'
            '\n\n\n{}\n'
        ).format(url, self.encode(j).decode('utf-8'))

    def encode(self, s):
        a = AES.new(self.key, AES.MODE_ECB)
        # Ensure s is bytes for encryption
        if isinstance(s, str):
            s = s.encode('utf-8')
        res = a.encrypt(s)
        return base64.b64encode(res)

    def decode(self, data):
        decoded = base64.b64decode(data)
        a = AES.new(self.key, AES.MODE_ECB)
        return a.decrypt(decoded)
