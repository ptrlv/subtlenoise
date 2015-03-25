#!/usr/bin/env python

"""
Subscribe to messages from the forwarder (fwdr.py) then does funky stuff
and sends OSC commands to Renoise (or whatever audio rendering engine)
"""

from datetime import timedelta, datetime
from optparse import OptionParser
import fileinput
import hashlib
import json
import logging
import random
import sys
import time
import zmq
import OSC

c = OSC.OSCClient()
note_on = OSC.OSCMessage(address='/renoise/trigger/note_on')
note_off = OSC.OSCMessage(address='/renoise/trigger/note_off')

def setup():
    global options
    global args
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.set_defaults(quiet=False)
    parser.set_defaults(debug=False)
    parser.set_defaults(server="localhost")
    parser.set_defaults(port=5510)
    parser.add_option("-m", action="store_true", help="mute mode, don't send OSC messages", dest="muteosc")
    parser.add_option("-f", action="store_true", help="filter messages, allow only PING", dest="ping")
    parser.add_option("-d", action="store_true", help="debug mode", dest="debug")
    parser.add_option("-t", action="store_true", help="test mode send OSC ping on every message", dest="test")
    parser.add_option("-v", action="store_true", help="verbosity, write incoming and OSC messages to stdout", dest="verbose")
    parser.add_option("-s", help="servername to send messages (default=localhost)", dest="server")
    parser.add_option("-p", help="port number on server (default=5510)", dest="port")
    (options, args) = parser.parse_args()
    loglevel = 'WARNING'
    if options.verbose:
        loglevel = 'INFO'
    if options.debug:
        loglevel = 'DEBUG'

    logger = logging.getLogger()
    logger.setLevel(logging._levelNames[loglevel])
    fmt = '[DJ:%(levelname)s %(asctime)s] %(message)s'
    formatter = logging.Formatter(fmt, '%T')
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.handlers = []
    logger.addHandler(handler)

    return (options, args)

def main():
    (options, args) = setup()
    context = zmq.Context()

    # subscribe to fwdr
    logging.debug("Connecting to fwdr...%s:%d" % (options.server, options.port))
    socket = context.socket(zmq.SUB)
    socket.hwm = 10
    socket.connect("tcp://%s:%d" % (options.server, options.port))

    # Subscribe to limited msgs or empty string for all msgs
    filter = '' 
    socket.setsockopt(zmq.SUBSCRIBE, filter)

    try:
        c.connect(('127.0.0.1', 57120))
    except:
        raise


    if options.test:
        note = 30
        inst = 4
        track = 0 
        velocity = 64
        txt = 'startup note_on:', inst, track, note, velocity
        logging.info(txt)
        noteon(inst, track, note, velocity)
        time.sleep(2)
        txt = 'startup note_off:', inst, track, note, velocity
        logging.info(txt)
        noteoff(inst, track, note)

# using OSCBundle is more natural, just get timeTags to work
#        bundle = OSC.OSCBundle()
#        oscmsg = OSC.OSCMessage(address='/renoise/trigger/note_off')
#        oscmsg.append([inst, track, note])
#        bundle.append(oscmsg)
#        bundle.setTimeTag(time.time()+3)
#        c.send(bundle)
#        bundle.clearData()

    # Process each msg
    rate = 50
    note = 60
    thisnote = 60
    inst = 0
    track = 1 
    velocity = 127
    logging.debug('Entering socket loop')
    while True:
        # if content is parsable as json then the content is converted
        # to a python object via json.loads, hopefully a dict 
        # if not parsable the a dict is created with key 'content'
        try:
            content = socket.recv()
            msg = json.loads(content)
        except ValueError:
            msg = {'content': content}
        except KeyboardInterrupt:
            logging.info("Keyboard interrupt, closing OSCClient")
            oscmsg = OSC.OSCMessage(address='/renoise/transport/panic')
            c.send(oscmsg)
            c.close()
            return 1
        except KeyError:
            pass
        except:
            logging.error(content)
            raise
            
        logging.debug("RAW: %s" % content)
        logging.debug(msg)

        if options.test:
            # send a ping on every incoming msg
            note = 60
            inst = 1
            oscmsg = OSC.OSCMessage(address='/renoise/trigger/note_on')
            oscmsg.append([inst, track, note, 127])
            c.send(oscmsg)
            logging.info(oscmsg)
            oscmsg.clearData()
            continue

        if options.ping:
            if 'PING' in msg.get('content',''):
                # send a ping on select msgs
                note = 40
                inst = 1
                oscmsg = OSC.OSCMessage(address='/renoise/trigger/note_on')
                oscmsg.append([inst, track, note, 127])
                logging.info(oscmsg)
                if options.muteosc: continue
                c.send(oscmsg)
                oscmsg.clearData()
                continue
            else:
                continue
        if options.debug: pass

        if 'meter' in msg.get('tags', []):
            rate = msg.get('events.rate_1m',rate)
            #
            bundle = OSC.OSCBundle()
            oscmsg = OSC.OSCMessage()
            previousnote = thisnote
            thisnote = int(rate) + 20
            meterinst = 7
            metertrack = 2
            velocity = 64
            oscmsg = OSC.OSCMessage(address='/renoise/trigger/note_off')
            oscmsg.append([meterinst, metertrack, previousnote])
            bundle.append(oscmsg)
            oscmsg = OSC.OSCMessage(address='/renoise/trigger/note_on')
            oscmsg.append([meterinst, metertrack, thisnote, velocity])
            bundle.append(oscmsg)
            if 'meter' in args:
                txt = 'RATE:',rate, meterinst, metertrack, thisnote, velocity
                logging.info(txt)
                if not options.muteosc: c.send(bundle)
            bundle.clearData()

        # demo has these instruments:
        # 1. dh_perc_click_signal
        # 2. ech_perc_vinyltriangle
        # 3. dh_perc_nu_dropdown
        # 4. Pad - VP - 330 Stringer
        # 5. dh_perc_shake_chimes
        # 6. Noise - Turbine   (Instr./Elements)
        # 7. Noise - 100Hz     
        # 8. 
        # 9. Pad - Mind War
        #10. dh_kick_sub_pitchy

        # track assignment is:
        # 0. testing
        # 1. apache
        # 2. meter
        if msg.get('type', None) == 'apache':
            if msg['response'] in ['200']:
                note = max(0, int(rate))
                note = random.randint(50,60)
                note = 50
                inst = 1
                velocity = 32
                if '200' in args:
                    txt = '200:', inst, track, note, velocity
                    logging.info(txt)
                    noteon(inst, track, note, velocity)
            elif msg['response'] in ['201']:
                note = max(10, int(rate) - 40)
                note = random.randint(25,35)
                note = 30
                inst = 2
                velocity = 16
                if '201' in args:
                    txt = '201:', inst, track, note, velocity
                    logging.info(txt)
                    noteon(inst, track, note, velocity)
            elif msg['response'] in ['404', '400']:
                note = 40
                note = random.randint(40,55)
                inst = 10
                velocity = 96
                if '4xx' in args:
                    txt = '404:', inst, track, note, velocity, msg['request'], msg['clientip']
                    logging.info(txt)
                    noteon(inst, track, note, velocity)
            elif msg['response'] in ['500']:
                logging.info(msg)
                note = 40
                inst = 3
                velocity = 127
                if '5xx' in args:
                    txt = '500:', inst, track, note, velocity
                    logging.info(txt)
                    noteon(inst, track, note, velocity)
            else:
                txt = 'unhandled', msg['response']
                logging.warn(txt)
                logging.debug(msg)
                continue
            
def noteon(inst, track, note, velocity):
    """
    Send OSC note_on message
    """
    note_on.append([inst, track, note, velocity])
    if options.muteosc:
        logging.info(note_on)
        note_on.clearData()
        return

    logging.debug(note_on)
    try:
        c.send(note_on)
        note_on.clearData()
    except OSC.OSCClientError:
        logging.error('OSCClientError: too bad')
        return 1
            
def noteoff(inst, track, note):
    """
    Send OSC note_off message
    """
    note_off.append([inst, track, note])
    if options.muteosc:
        logging.info(note_off)
        note_off.clearData()
        return

    logging.debug(note_off)
    try:
        c.send(note_off)
        note_off.clearData()
    except OSC.OSCClientError:
        logging.error('OSCClientError: too bad')
        return 1

if __name__ == "__main__":
    sys.exit(main())
