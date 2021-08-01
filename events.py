#!/usr/bin/env python

from __future__ import unicode_literals, print_function
from datetime import datetime
from base64 import b64decode
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid
from smtplib import SMTP
from glob import iglob
import os, json, ticket, codecs

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
        with open(self.get_ticket_filename(ticket_id), 'w') as ticket_file:
            json.dump(values, ticket_file)
        return ticket_id

    def send_ticket(self, values, url):
        content = MAIL_FMT.format(self=self, name=values['name']['value'], url=url)
        recipient = values['email']['value']
        subject = u'Your {self.name} ticket'.format(self=self)
        self.send_mail(subject, recipient, content)

    def send_news(self, subject, content_file):
        with codecs.open(content_file, 'r', 'utf-8') as cf:
            content = cf.read()
        for filename in iglob(os.path.join(self.eid, '*.json')):
            with open(filename, 'rb') as ticket:
                values = json.load(ticket)
            recipient = values['email']['value']
            self.send_mail(subject, recipient, content.format(
                self=self, name=values['name']['value']))
            print('sent to', recipient)

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
        return os.path.join(os.path.dirname(__file__), self.eid, ticket_id) + '.json'

    def get_vending_machine(self):
        return ticket.VendingMachine(b64decode(self.secret.encode('ascii')))


def get(eid=None):
    events = get_config('events')
    if eid is None:
        return [(iid, Event(iid, data)) for iid, data in events.items()]
    else:
        return Event(eid, events[eid])

def get_config(key):
    with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'rb') as config_file:
        return json.load(config_file)[key]

def main():
    from sys import argv, stderr
    if len(argv) < 5 or argv[1] != 'news':
        print('Usage: {0} news <event> <subject> <mail.txt>'.format(argv[0]),
                file=stderr)
        exit(1)
    else:
        try:
            event = get(argv[2])
        except KeyError:
            print('Invalid event name')
            exit(1)
        else:
            event.send_news(argv[3].decode('utf-8'), argv[4])


if __name__ == '__main__':
    main()
