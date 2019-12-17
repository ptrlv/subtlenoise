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

def hashToP_C(hashable):
    #Hashes an input and returns a pan value from -1 to 1.
    num = hash(hashable)
    
    if num == 0:
        #print("Num is 0.")
        pan = 0
    else:
        digits = int(math.log10(abs(num)))+1
        pan = num * 10**(digits*-1)

    sign = 1
    if num % 2 == 0:
        sign = -1

    cutoff = 95 + 15*sign*abs(pan)

    return (pan, cutoff)

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

        '''
        if 'fault' in content:
            if isPrinting:
                print(bcolors.FAIL+content+bcolors.ENDC)
        elif isPrinting:
            print(content)
        '''

        # send a ping on every incoming msg
        if args.test:
            msg = osc_message_builder.OscMessageBuilder(address = "/ping")
            logging.info("/ping {}".format(content))
            client.send(msg.build())
    
        if args.mute: return
        """
        if 'running' in content:
            duration = int(content.split()[1])
            msg = osc_message_builder.OscMessageBuilder(address = "/starting")
            msg.add_arg(duration)
            client.send(msg.build())
        """
        if 'exiting' in content:
            duration = int(content.split()[1])
            msg = osc_message_builder.OscMessageBuilder(address = "/goodness")
            #msg.add_arg(duration)

            #Takes log of duration and checks which midi note will be played to represent it.
            #8 bins for durations to be fit into. They are the notes of the harmonic series.
            
            #scale = [33, 45, 52, 57, 61, 64, 69, 71] #Shortest = lowest
            scale = [71, 69, 64, 61, 57, 52, 45, 33] #Shortest = highest

            logTime = math.log(duration)

            if duration <= 200000:
                midi = 7055 - (7000/math.log(200000))*logTime
            else:
                midi = 55

            # midi = 0
            # if logTime <= 4.0:
            #     midi = scale[0]
            # elif 4.0 <= logTime <= 5.0:
            #     midi = scale[1]
            # elif 5.0 <= logTime <= 6.0:
            #     midi = scale[2]
            # elif 6.0 <= logTime <= 7.0:
            #     midi = scale[3]
            # elif 7.0 <= logTime <= 8.0:
            #     midi = scale[4]
            # elif 8.0 <= logTime <= 9.0:
            #     midi = scale[5]
            # elif 9.0 <= logTime <= 10.0:
            #     midi = scale[6]
            # elif 10.0 <= logTime:
            #     midi = scale[7]
            # else:
            #     print("ERROR BIN SYSTEM NOT WORKING.")

            msg.add_arg(midi)
            msg.add_arg(duration)

            toSplit = content.split()[-1]
            try:
                toHash = toSplit.split(':')[0]
                #print('{' + toHash + '}')
            except:
                print('ERROR BAD HASH')
            
            params = hashToP_C(toHash)
            #print(params)
            msg.add_arg(params[0])
            msg.add_arg(params[1])

            client.send(msg.build())

        if 'fault' in content:
            duration = int(content.split()[1])
            msg = osc_message_builder.OscMessageBuilder(address = "/badness")
            msg.add_arg(duration)
            client.send(msg.build())

    except ValueError:
        msg = "ValueError: {}".format(content)
        logging.warning(msg)
        raise
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

    #Checks whether input stream should be paused.
    global isPrinting
    isPrinting = True

    args = setup()

    client = udp_client.UDPClient(args.ip, args.port)

    mqttc = mqtt.Client()
    mqttc.connect(HOST, PORT)
    mqttc.subscribe('wrapper') #Changed from test to wrapper.
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
