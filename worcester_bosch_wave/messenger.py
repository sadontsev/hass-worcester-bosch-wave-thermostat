import base64

import sleekxmpp
from Crypto.Cipher import AES
from utils import get_md5

from worcester_bosch_wave.constants import SECRET


class WaveMessenger(sleekxmpp.ClientXMPP):
    def __init__(self, serial_number, access_code, password, message):

        jid = f'rrccontact_{serial_number}@wa2-mz36-qrmzh6.bosch.de'
        connection_password = f'Ct7ZR03b_{access_code}'

        sleekxmpp.ClientXMPP.__init__(self, jid, connection_password)

        self.recipient = f'rrcgateway_{serial_number}@wa2-mz36-qrmzh6.bosch.de'
        self.msg = message

        self.add_event_handler('session_start', self.start)
        self.add_event_handler('message', self.message)

        self.connected = False

        abyte_1 = get_md5(access_code.encode() + SECRET)
        abyte_2 = get_md5(SECRET + password.encode())

        self.key = abyte_1 + abyte_2

    def connect(self, **kwargs):
        self.connected = True
        return sleekxmpp.ClientXMPP.connect(
            self, ('wa2-mz36-qrmzh6.bosch.de', 5222), use_ssl=False, use_tls=False
        )

    def disconnect(self, **kwargs):
        self.connected = False
        return sleekxmpp.ClientXMPP.disconnect(self)

    def run(self):
        self.connect()
        self.go()
        self.process(block=True)

    def start(self):
        self.send_presence()
        self.get_roster()

    def go(self):
        if not self.connected:
            self.connect()

        self.send_message(mto=self.recipient, mbody=self.msg, mtype='chat')

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
        res = a.encrypt(s)
        return base64.b64encode(res)

    def decode(self, data):
        decoded = base64.b64decode(data)
        a = AES.new(self.key, AES.MODE_ECB)
        return a.decrypt(decoded)
