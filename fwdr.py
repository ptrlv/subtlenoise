#!/usr/bin/env python

"""
Forwarder device listens to publishers on port 5500 and re-publishes
on port 5510
"""

from datetime import timedelta, datetime
from optparse import OptionParser
import fileinput
import logging
import sys
import zmq

def setup():
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.set_defaults(quiet=False)
    parser.set_defaults(debug=False)
    parser.add_option("-q", help="quiet mode", dest="quiet", action="store_true")
    parser.add_option("-d", help="debug mode", dest="debug", action="store_true")
    (options, args) = parser.parse_args()
    loglevel = 'INFO'
    if options.quiet:
        loglevel = 'WARNING'
    if options.debug:
        loglevel = 'DEBUG'

    logger = logging.getLogger()
    logger.setLevel(logging._levelNames[loglevel])
    fmt = '[MSG:%(levelname)s %(asctime)s] %(message)s'
    formatter = logging.Formatter(fmt, '%T')
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.handlers = []
    logger.addHandler(handler)

    return options

def main():
    options = setup()
    try:
        context = zmq.Context()

        # Socket facing publishers
        frontend = context.socket(zmq.SUB)
        frontend.setsockopt(zmq.SUBSCRIBE, "")
        frontend.bind("tcp://*:5500")

        # Socket facing subscribers
        backend = context.socket(zmq.PUB)
        backend.bind("tcp://*:5510")

        logging.debug('Starting forwarder device...')
        zmq.device(zmq.FORWARDER, frontend, backend)
    except Exception, e:
        print e
    finally:
        pass
        frontend.close()
        backend.close()
        context.term()

if __name__ == "__main__":
    sys.exit(main())
