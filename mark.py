#!/usr/bin/env python

from datetime import datetime
from optparse import OptionParser
import logging
import zmq
import random
import sys
import time

"""
Publish a zeromq message
"""

def setup():
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.set_defaults(quiet=False)
    parser.set_defaults(debug=False)
    parser.set_defaults(server="localhost")
    parser.set_defaults(port=5500)
    parser.add_option("-q", help="quiet mode", dest="quiet")
    parser.add_option("-d", action="store_true", help="debug mode", dest="debug")
    parser.add_option("-s", help="servername to connect to (default=localhost)", dest="server")
    parser.add_option("-p", help="port number on server (default=5510)", dest="port")
    (options, args) = parser.parse_args()
    loglevel = 'INFO'
    if options.quiet:
        loglevel = 'WARNING'
    if options.debug:
        loglevel = 'DEBUG'

    logger = logging.getLogger()
    logger.setLevel(logging._levelNames[loglevel])
    fmt = '[PUB:%(levelname)s %(asctime)s] %(message)s'
    formatter = logging.Formatter(fmt, '%T')
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.handlers = []
    logger.addHandler(handler)

    return options, args

def main():
    options, args = setup()
    context = zmq.Context()

    # publish to fwdr
    logging.info("Connecting to fwdr...%s:%d" % (options.server, options.port))
    socket = context.socket(zmq.PUB)
    socket.hwm = 10
    socket.connect("tcp://%s:%d" % (options.server, options.port))

    time.sleep(1)
    
    msg = ' '.join(args)
    socket.send(msg)

if __name__ == "__main__":
    sys.exit(main())
