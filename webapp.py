#!/usr/bin/env python

from flask import Flask, render_template, abort, request, redirect, url_for
from subprocess import check_output
from base64 import b64encode
from email_validation import valid_email_address
import events

app = Flask(__name__)

TICKET_FIELDS = (
        ('name', 'Name', bool),
        ('email', 'E-mail', valid_email_address),
        ('notes', 'Notes', None),
        )

@app.route('/')
def event_list():
    return render_template('event_list.html', event_list=events.get())

@app.route('/<eid>', methods=['GET', 'POST'])
def show_event(eid):
    try:
        event = events.get(eid)
    except KeyError:
        abort(404)
    else:
        values = {}
        if request.method == 'POST':
            all_fields_valid = True
            for name, _, validator in TICKET_FIELDS:
                value = request.form.get(name, '')
                error = validator is not None and not validator(value)
                values[name] = {'value': value, 'error': error}
            if not any(field['error'] for field in values.itervalues()):
                ticket = event.generate_ticket(values)
                ticket_url = url_for('show_ticket', eid=eid, ticket=ticket, _external=True)
                event.send_mail(values, ticket_url)
                return redirect(ticket_url)
        return render_template('show_event.html', event=event,
                fields=TICKET_FIELDS, values=values)

@app.route('/<eid>/<ticket>.html')
def show_ticket(eid, ticket):
    try:
        event = events.get(eid)
        event.verify_ticket(ticket)
    except (KeyError, AssertionError):
        abort(404)
    else:
        ticket_png = b64encode(check_output(['qrencode', '-t', 'PNG', '-s', '8',
            '-o', '-', '-i', ticket]))
        return render_template('show_ticket.html', event=event,
                ticket_id=ticket, ticket_png=ticket_png)

if __name__ == '__main__':
    app.run(debug=True)
