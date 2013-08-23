#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest, ticket

TICKET_VALUES = (
        '\x01' * ticket.FULL_LEN,
        '\xFF' * ticket.FULL_LEN,
        ''.join(chr(i) for i in xrange(ticket.FULL_LEN)),
        )


class TestTicket(unittest.TestCase):
    def test_encode_decode(self):
        for ticket_value in TICKET_VALUES:
            encoded = ticket.encode(ticket_value)
            decoded = ticket.decode(encoded)
            self.assertEquals(ticket_value, decoded)

    def test_generate_verify(self):
        ticket.verify(ticket.generate())


if __name__ == '__main__':
    unittest.main()
