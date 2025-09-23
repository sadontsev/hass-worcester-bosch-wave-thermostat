import base64
import time
import logging
import slixmpp
from Crypto.Cipher import AES
from .utils import get_md5

from .constants import SECRET

_LOGGER = logging.getLogger(__name__)


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
        self.use_ssl = False
        self.auto_reconnect = False

        # State flags
        self.connected = False
        self.session_started = False
        self.message_sent = False
        self.response_received = False
        self.auth_failed = False

        # Event handlers
        self.add_event_handler('session_start', self._on_session_start)
        self.add_event_handler('message', self.message)  # overridden in subclass
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
        _LOGGER.debug("XMPP connected: %s", event)
        self.connected = True

    def _on_disconnected(self, event):
        _LOGGER.debug("XMPP disconnected: %s", event)
        self.connected = False

    def _on_failed_auth(self, event):
        _LOGGER.warning("XMPP authentication failed: %s", event)
        self.auth_failed = True

    def _on_stream_error(self, event):
        _LOGGER.error("XMPP stream error: %s", event)

    async def _on_session_start(self, event):
        _LOGGER.debug("XMPP session started")
        self.session_started = True
        self.send_presence()
        try:
            await self.get_roster()
        except Exception as e:
            _LOGGER.debug("get_roster failed: %s", e)
        self._send()

    # ---- Messaging ----
    def _send(self):
        _LOGGER.debug("Sending message to %s", self.recipient)
        self.send_message(mto=self.recipient, mbody=self.msg, mtype='chat')
        self.message_sent = True
        _LOGGER.debug("Message sent, waiting for response…")

    def set_message(self, url, value):
        j = '{"value":%s}' % (repr(value))
        remainder = len(j) % 16
        if remainder:
            j = j + '\x00' * (16 - remainder)
        enc = self.encode(j).decode('utf-8')
        content_length = len(enc)
        self.msg = (
            'PUT {} HTTP/1.0\n'
            'Content-Type: application/json\n'
            'Content-Length: {}\n'
            'User-Agent: NefitEasy\n'
            '\n\n\n{}\n'
        ).format(url, content_length, enc)

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
    def run(self, timeout: int = 30):
        """Blocking runner used by sync contexts.

        Connects, processes XMPP events, and disconnects on response or timeout.
        Returns True if a response was received.
        """
        _LOGGER.debug("Starting XMPP connection…")
        # Ensure flags reset for each run
        self.response_received = False
        self.auth_failed = False
        self.session_started = False
        self.message_sent = False

        # Start connection; slixmpp will finalize during process()
        try:
            # Use positional argument for broader slixmpp compatibility
            result = super().connect(('wa2-mz36-qrmzh6.bosch.de', 5222))
            # Some slixmpp versions return a coroutine for connect(); await it on our loop
            try:
                import asyncio as _asyncio
                if _asyncio.iscoroutine(result):
                    self.loop.run_until_complete(result)
                    success = True
                else:
                    success = bool(result)
            except Exception:
                success = bool(result)
        except Exception as e:
            _LOGGER.error("Connect error: %s", e)
            return False

        _LOGGER.debug("Connect initiated: %s", success)
        if not success:
            return False

        # Enforce timeout by scheduling a disconnect after N seconds
        try:
            self.loop.call_later(timeout, self._timeout_disconnect)
        except Exception as e:
            _LOGGER.debug("Failed to schedule timeout: %s", e)

        # Process events until disconnect (either on response, auth failure, or timeout)
        try:
            # Older/compatible API path
            self.process(forever=True)
        except AttributeError:
            # Fallback for slixmpp versions without process(): wait on the 'disconnected' future
            try:
                self.loop.run_until_complete(self.disconnected)
            except Exception as e:
                _LOGGER.debug("Fallback wait on 'disconnected' failed: %s", e)

        if self.auth_failed:
            _LOGGER.warning("Authentication failed during XMPP session")
            return False

        _LOGGER.debug("Finished processing. Response received: %s", self.response_received)
        return self.response_received

    def _timeout_disconnect(self):
        if not self.response_received and self.is_connected():
            _LOGGER.debug("Timeout reached, disconnecting…")
            self.disconnect()
