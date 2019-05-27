#!/usr/bin/python3

import sys
import logging

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/FLASKAPPS/")

#from app import app as application
from talismansoftwaresolutions import app as application
