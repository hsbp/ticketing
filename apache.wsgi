#!/usr/bin/env python

import inspect, os, sys

os.chdir(os.path.dirname(inspect.getfile(inspect.currentframe())))
sys.path.append(os.getcwd())

from webapp import app as application
