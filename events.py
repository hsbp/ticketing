#!/usr/bin/env python

from __future__ import unicode_literals
from datetime import datetime
from base64 import b64decode
import os, json, ticket

ISO_DATE_FMT = '%Y-%m-%d'

class Event(object):
    TEXT_KEYS = ('name', 'location', 'homepage', 'secret')
    DATE_KEYS = ('start', 'end')

    def __init__(self, eid, config):
        self.eid = eid
        for key in Event.TEXT_KEYS:
            setattr(self, key, config[key])
        for key in Event.DATE_KEYS:
            setattr(self, key, datetime.strptime(config[key], ISO_DATE_FMT).date())

    def generate_ticket(self, values):
        vm = self.get_vending_machine()
        ticket_id = ticket.encode(vm.generate())
        if not os.path.exists(self.eid):
            os.makedirs(self.eid)
        with file(self.get_ticket_filename(ticket_id), 'wb') as ticket_file:
            json.dump(values, ticket_file)
        return ticket_id

    def verify_ticket(self, ticket_id):
        vm = self.get_vending_machine()
        vm.verify(ticket.decode(ticket_id))
        if not os.path.exists(self.get_ticket_filename(ticket_id)):
            raise KeyError('Ticket file does not exist')

    def get_ticket_filename(self, ticket_id):
        return os.path.join(self.eid, ticket_id) + '.json'

    def get_vending_machine(self):
        return ticket.VendingMachine(b64decode(self.secret))


def get(eid=None):
    with file('config.json', 'rb') as config_file:
        config = json.load(config_file)
    if eid is None:
        return [(iid, Event(iid, data)) for iid, data in config['events'].iteritems()]
    else:
        return Event(eid, config['events'][eid])
