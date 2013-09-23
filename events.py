#!/usr/bin/env python

from __future__ import unicode_literals
from datetime import datetime
from base64 import b64decode
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid
from smtplib import SMTP
import os, json, ticket

ISO_DATE_FMT = '%Y-%m-%d'
MAIL_FMT = '''
Dear {name},
thanks for registering for a ticket to {self.name}. The event starts on {self.start} at {self.location}, and your ticket can be viewed or downloaded from {url} any time until {self.end}. Keep this URL private, as each ticket can be used only once, no matter how many copies are made. See the webpage ({self.homepage}) for more details about the event.

Regards,
{self.name} organizers
'''.strip()

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

    def send_ticket(self, values, url):
        content = MAIL_FMT.format(self=self, name=values['name']['value'], url=url)
        recipient = values['email']['value']
        subject = u'Your {self.name} ticket'.format(self=self)
        self.send_mail(subject, recipient, content)

    def send_mail(self, subject, recipient, content):
        cfg = get_config('smtp')
        smtp = SMTP(cfg.get('host', 'localhost'), cfg.get('port', 25))
        try:
            sender = cfg['from']
            msg = MIMEText(content, 'plain', 'utf-8')
            msg['To'] = recipient
            msg['From'] = self.name + ' <' + sender + '>'
            msg['Subject'] = subject
            msg['Date'] = formatdate(localtime=True)
            msg['Message-Id'] = make_msgid(self.eid)
            smtp.sendmail(sender, [recipient], msg.as_string(False))
        finally:
            smtp.quit()

    def verify_ticket(self, ticket_id):
        vm = self.get_vending_machine()
        vm.verify(ticket.decode(ticket_id))
        assert os.path.exists(self.get_ticket_filename(ticket_id))

    def get_ticket_filename(self, ticket_id):
        return os.path.join(self.eid, ticket_id) + '.json'

    def get_vending_machine(self):
        return ticket.VendingMachine(b64decode(self.secret))


def get(eid=None):
    events = get_config('events')
    if eid is None:
        return [(iid, Event(iid, data)) for iid, data in events.iteritems()]
    else:
        return Event(eid, events[eid])

def get_config(key):
    with file('config.json', 'rb') as config_file:
        return json.load(config_file)[key]
