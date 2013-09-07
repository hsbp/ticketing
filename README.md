Ticket generator
================

Setup
-----

Generate a secret (symmetric) signing key, for example by running the command below.

	$ dd if=/dev/random bs=16 count=2 | base64

Create a configuration file named `config.json` based on `config.example.json`
and use the secret generated above there. The keys used for events must either
exist as a writable subdirectory or the user running the Python process must
have the privileges necessary to create subdirectories for web vending to work.

If you serve it over SSL, you can put information in plain text into a file
named `certinfo.txt`, which will be displayed under `/cert`.

License
-------

The whole project is available under MIT license.

Dependencies
------------

 - Python 2.x (tested on 2.7.5)
 - Flask (Debian/Ubuntu package: `python-flask`)
 - qrencode (Debian/Ubuntu package: `qrencode`)
 - py_email_validation (https://pypi.python.org/pypi/py_email_validation)
