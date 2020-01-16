#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from six.moves import range
from six import int2byte
import unittest, ticket

TICKET_VALUES = (
        b'\x01' * ticket.FULL_LEN,
        b'\xFF' * ticket.FULL_LEN,
        b''.join(int2byte(i) for i in range(ticket.FULL_LEN)),
        )


class TestTicket(unittest.TestCase):
    def setUp(self):
        self.vm = ticket.VendingMachine(b"TestingSecret23")

    def test_encode_decode(self):
        for ticket_value in TICKET_VALUES:
            encoded = ticket.encode(ticket_value)
            decoded = ticket.decode(encoded)
            self.assertEquals(ticket_value, decoded)

    def test_generate_verify(self):
        self.vm.verify(self.vm.generate())


if __name__ == '__main__':
    unittest.main()
