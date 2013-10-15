#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/home/ubuntu/deaddrop")

from deaddrop import app as application
