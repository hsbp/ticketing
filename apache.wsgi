#!/usr/bin/env python

import inspect, os, sys

os.chdir(os.path.dirname(inspect.getfile(inspect.currentframe())))
sys.path.append(os.getcwd())

from web import app as application
