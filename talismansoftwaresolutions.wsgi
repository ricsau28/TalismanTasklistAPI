#!/usr/bin/python3
activate_this = '/var/www/FLASKAPPS/talismansoftwaresolutions/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

import sys
import logging

logging.basicConfig(stream=sys.stderr)

sys.path.insert(0, '/var/www/FLASKAPPS/')

from talismansoftwaresolutions import app as application