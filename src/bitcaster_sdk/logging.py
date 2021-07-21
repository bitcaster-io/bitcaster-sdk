import logging
import sys


logger = logging.getLogger('bitcaster_sdk')

h = logging.StreamHandler(sys.stdout)
h.flush = sys.stdout.flush
logger.addHandler(h)
