import hashlib


def get_md5(data):
    m = hashlib.md5()
    m.update(data)

    return m.digest()


def parse_on_off(s):
    return s == 'on'
