from .messenger import WaveMessenger


class WaveSet(WaveMessenger):
    current_temp = None
    set_point = None
    is_boiler_on = None

    def __init__(self, serial_number, access_code, password):
        super().__init__(serial_number, access_code, password, '')

    def message(self, msg):
        """
        Process a message once it has been received
        """
        body = msg.get('body', '')
        if 'No Content' in body or 'OK' in body:
            # Successful PUT responses often return 204 No Content
            self.response_received = True
            self.disconnect()
        elif 'Bad Request' in body or '400' in body:
            # Log and disconnect; let caller interpret as failure
            try:
                import logging
                logging.getLogger(__name__).warning('WaveSet Bad Request response: %s', body[:120])
            except Exception:
                pass
            self.response_received = False
            self.disconnect()

    def post_message(self, url, value):
        self.set_message(url, value)
        return self.run()
