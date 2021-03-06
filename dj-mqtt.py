#!/usr/bin/env python3

"""
Subscribe to MQTT message and act on these by sending OSC commands
to an audio rendering engine
"""

import argparse
import json
#import hashlib
import logging
import random
import time
import socket
import sys

import paho.mqtt.client as mqtt
#from pythonosc import osc_bundle
from pythonosc import osc_message_builder
from pythonosc import udp_client

PORT=1883
HOST='148.88.67.14'
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def on_message(mosq, userdata, msg):
    global args
    global client

    content = msg.payload.decode("utf-8").rstrip()[:140]
    try: 
        if args.filter and any(filter in content for filter in args.filter):
            msg = "FILTERED: {}".format(content)
            logging.info(msg)
            return

        if 'fault' in content:
            print(bcolors.FAIL+content+bcolors.ENDC)
        else:
            print(content)

        # send a ping on every incoming msg
        if args.test:
            msg = osc_message_builder.OscMessageBuilder(address = "/ping")
            logging.info("/ping {}".format(content))
            client.send(msg.build())
    
        if args.mute: return

        if 'running' in content:
            duration = int(content.split()[1])
            msg = osc_message_builder.OscMessageBuilder(address = "/starting")
            msg.add_arg(duration)
            client.send(msg.build())

        if 'exiting' in content:
            duration = int(content.split()[1])
            msg = osc_message_builder.OscMessageBuilder(address = "/goodness")
            msg.add_arg(duration)
            client.send(msg.build())

        if 'fault' in content:
            duration = int(content.split()[1])
            msg = osc_message_builder.OscMessageBuilder(address = "/badness")
            msg.add_arg(duration)
            client.send(msg.build())

    except ValueError:
        msg = "ValueError: {}".format(content)
        logging.warning(msg)
    except:
        raise

def setup():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1", help="The ip of the OSC server")
    parser.add_argument("--port", type=int, default=4559, help="The port the OSC server is listening on")
    parser.add_argument('-m', '--mute', action='store_true', help="mute mode, don't send OSC messages")
    parser.add_argument('-d', '--debug', action='store_true', help="debug mode")
    parser.add_argument('-t', '--test', action='store_true', help="test mode send OSC ping on every message")
    parser.add_argument('-v', '--verbose', help='output stuff', action="store_true")
    parser.add_argument('-f', '--filter', nargs='+', default=[], help='filter on string, max 3 filters')
    args = parser.parse_args()

    level = logging.WARNING
    if args.verbose: level = logging.INFO 
    if args.debug: level = logging.DEBUG 
    logging.basicConfig(format='%(levelname)s:%(message)s', level=level)

    return args

def main():
    global args
    global client
    args = setup()

    client = udp_client.UDPClient(args.ip, args.port)

    mqttc = mqtt.Client()
    mqttc.connect(HOST, PORT)
    mqttc.subscribe('wrapper')
    mqttc.on_message = on_message
    while True:
        mqttc.loop()

if __name__ == "__main__":
    sys.exit(main())
