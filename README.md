Ticket generator
================

Setup
-----

Generate a secret (symmetric) signing key, for example by running the command below.

	$ dd if=/dev/random bs=16 count=2 | base64

Create a configuration file named `config.json` based on `config.example.json`
and use the secret generated above there.

License
-------

The whole project is available under MIT license.

Dependencies
------------

 - Python 2.x (tested on 2.7.5)
 - Flask (Debian/Ubuntu package: `python-flask`)
 - qrencode (Debian/Ubuntu package: `qrencode`)
