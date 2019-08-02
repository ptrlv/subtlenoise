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
import math
import os

import paho.mqtt.client as mqtt
#from pythonosc import osc_bundle
from pythonosc import osc_message_builder
from pythonosc import udp_client

#Colorama is a workaround to allow windows' terminal to interpret ANSI messages.
#Should not affect other OSs.
from colorama import init
init()

#Allows listening for keyboard input without pausing program.
import keyboard

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

def hashToPan(hashable):
    #For testing wants to make a tuple containing job site string, hash of job site and pan value.
    #Create set of these tuples and then update it every time a new value is present.
    #If updating set, append a text file with the new addition.

    global testSet

    num = hash(hashable)
    digits = int(math.log10(abs(num)))+1

    pan = num * 10**(digits*-1)

    tup = (hashable, num, pan)

    if tup not in testSet:
        testSet.add(tup)
        with open("PanList.txt", "a+") as myfile:
            myfile.write(str(tup[0]) + '\t' + str(tup[1]) + '\t' + str(tup[2]) + '\n')

def on_message(mosq, userdata, msg):
    global args
    global client

    global isPrinting #Checks whether input stream should be paused.

    content = msg.payload.decode("utf-8").rstrip()[:140]
    try: 
        if args.filter and any(filter in content for filter in args.filter):
            msg = "FILTERED: {}".format(content)
            logging.info(msg)
            return

        #Better implementation of printing check.
        if isPrinting:
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

        if 'exiting' in content:
            toSplit = content.split()[-1]
            toHash = toSplit.split(':')[0]
            hashToPan(toHash)


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

    #Sets up the set for checking for unique hashes and deletes the old list if there is one.
    global testSet
    testSet = set()
    try:
        os.remove("PanList.txt")
    except:
        pass

    #Checks whether input stream should be paused.
    global isPrinting
    isPrinting = True

    args = setup()

    client = udp_client.UDPClient(args.ip, args.port)

    mqttc = mqtt.Client()
    mqttc.connect(HOST, PORT)
    mqttc.subscribe('test')
    mqttc.on_message = on_message
    while True:
        mqttc.loop()
        #Checks for if pause key 'p' or resume key 'r' have been pressed.
        try:
            #Stops printing incoming mqtt messages to terminal.
            if keyboard.is_pressed('ctrl+shift+p') and isPrinting == True: #isPrinting check stops multiple prints on key hold.
                print(bcolors.OKGREEN+"Pause feed."+bcolors.ENDC)
                isPrinting = False

            #Resumes printing incoming mqtt messages to terminal.
            if keyboard.is_pressed('ctrl+shift+r') and isPrinting == False:
                print(bcolors.OKGREEN+"Resume feed."+bcolors.ENDC)
                isPrinting = True

            #Stops sending osc messages to SonicPi.
            if keyboard.is_pressed('ctrl+shift+m') and args.mute == False:
                print(bcolors.OKGREEN+"Muting program."+bcolors.ENDC)
                args.mute = True

            #Resumes sending osc messages to SonicPi.
            if keyboard.is_pressed('ctrl+shift+n') and args.mute == True:
                print(bcolors.OKGREEN+"Unmuting program."+bcolors.ENDC)
                args.mute = False

        except:
            pass

if __name__ == "__main__":
    sys.exit(main())
