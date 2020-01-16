#!/usr/bin/env python

from __future__ import unicode_literals, print_function
from uuid import uuid4, UUID
from hashlib import sha256
from binascii import hexlify, unhexlify
import hmac

UUID_LEN = 16
HMAC_LEN = 10
FULL_LEN = UUID_LEN + HMAC_LEN

class VendingMachine(object):
    def __init__(self, secret):
        self.secret = secret

    def generate(self):
        tid = uuid4().bytes
        return tid + self.sign(tid)

    def verify(self, ticket):
        tid = ticket[:UUID_LEN]
        signature = ticket[UUID_LEN:]
        assert self.sign(tid) == signature
        parsed = UUID(bytes=ticket[:UUID_LEN])
        assert parsed.version == 4
        return parsed

    def sign(self, tid):
        return hmac.new(self.secret, tid, sha256).digest()[:HMAC_LEN]

def encode(ticket):
    return base36encode(int(hexlify(ticket), 16))

def base36encode(number):
    alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    base36 = ''
    while number:
        number, i = divmod(number, 36)
        base36 = alphabet[i] + base36

    return base36 or alphabet[0]

def decode(qr):
    fmt = '{0:0' + str(FULL_LEN * 2) + 'x}'
    hexed = fmt.format(base36decode(qr))
    return unhexlify(hexed)

def base36decode(number):
    return int(number, 36)

def console_test(): # pragma: nocover
    vm = VendingMachine(b'WeakSecret42')
    ticket = vm.generate()
    print('TICKET', hexlify(ticket))
    qr = encode(ticket)
    print('QRCODE', qr)
    decoded = decode(qr)
    print('DECODE', hexlify(decoded))
    assert decoded == ticket
    print('VERIFY', vm.verify(decoded))


if __name__ == '__main__':
    console_test() # pragma: nocover
