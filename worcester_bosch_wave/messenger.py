import base64
import time
import slixmpp
from Crypto.Cipher import AES
from .utils import get_md5

from .constants import SECRET


class WaveMessenger(slixmpp.ClientXMPP):
    """Low-level XMPP messenger for Worcester Bosch Wave."""

    def __init__(self, serial_number, access_code, password, message):
        # Clean inputs
        serial_number = serial_number.replace(' ', '').strip('"')
        access_code = access_code.replace(' ', '').strip('"')
        password = password.strip('"')

        jid = f'rrccontact_{serial_number}@wa2-mz36-qrmzh6.bosch.de'
        connection_password = f'Ct7ZR03b_{access_code}'

        super().__init__(jid, connection_password)

        self.recipient = f'rrcgateway_{serial_number}@wa2-mz36-qrmzh6.bosch.de'
        self.msg = message

        # Bosch turned off SSL/TLS in 2018
        self.use_tls = False
        self.auto_reconnect = False

        # State flags
        self.connected = False
        self.session_started = False
        self.message_sent = False
        self.response_received = False
        self.auth_failed = False

        # Event handlers
        self.add_event_handler('session_start', self._on_session_start)
        self.add_event_handler('message', self.message)
        self.add_event_handler('connected', self._on_connected)
        self.add_event_handler('disconnected', self._on_disconnected)
        self.add_event_handler('failed_auth', self._on_failed_auth)
        self.add_event_handler('stream_error', self._on_stream_error)

        # Crypto key
        abyte_1 = get_md5(access_code.encode() + SECRET)
        abyte_2 = get_md5(SECRET + password.encode())
        self.key = abyte_1 + abyte_2

    # ---- Event handlers ----
    def _on_connected(self, event):
        print(f"🔗 XMPP connected: {event}")
        self.connected = True

    def _on_disconnected(self, event):
        print(f"🔌 XMPP disconnected: {event}")
        self.connected = False

    def _on_failed_auth(self, event):
        print(f"❌ XMPP authentication failed: {event}")
        self.auth_failed = True

    def _on_stream_error(self, event):
        print(f"⚠️ XMPP stream error: {event}")

    async def _on_session_start(self, event):
        print("🚀 XMPP session started")
        self.session_started = True
        self.send_presence()
        try:
            await self.get_roster()
        except Exception as e:
            print(f"⚠️ get_roster failed: {e}")
        self._send()

    # ---- Messaging ----
    def _send(self):
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
        if isinstance(s, str):
            s = s.encode('utf-8')
        res = a.encrypt(s)
        return base64.b64encode(res)

    def decode(self, data):
        decoded = base64.b64decode(data)
        a = AES.new(self.key, AES.MODE_ECB)
        return a.decrypt(decoded)

    # ---- Runner ----
    def run(self, timeout: int = 20):
        """Blocking runner used by sync contexts.

        Connects, processes XMPP events, and disconnects on response or timeout.
        Returns True if a response was received.
        """
        print("🔌 Starting XMPP connection…")
        # Ensure flags reset for each run
        self.response_received = False
        self.auth_failed = False
        self.session_started = False
        self.message_sent = False

        # Start async connection; slixmpp will finalize during process()
        try:
            success = super().connect(address=('wa2-mz36-qrmzh6.bosch.de', 5222))
        except Exception as e:
            print(f"❌ Connect error: {e}")
            return False

        print(f"� Connect initiated: {success}")

        if not success:
            return False

        # Enforce timeout by scheduling a disconnect after N seconds
        try:
            self.loop.call_later(timeout, self._timeout_disconnect)
        except Exception as e:
            print(f"⚠️ Failed to schedule timeout: {e}")

        # Process events until disconnect (either on response, auth failure, or timeout)
        try:
            self.process(forever=False)
        finally:
            if self.is_connected():
                self.disconnect()

        if self.auth_failed:
            print("❌ Authentication failed during XMPP session")
            return False

        print(f"🏁 Finished processing. Response: {self.response_received}")
        return self.response_received

    def _timeout_disconnect(self):
        if not self.response_received and self.is_connected():
            print("⏱️ Timeout reached, disconnecting…")
            self.disconnect()
