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

def on_message(mosq, userdata, msg):
    global args
    global client

    global isPrinting #Checks whether input stream should be paused.

    global paramData #Data which is going to be sonified
    global key #Which parts of list to grab from message

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

        chunks = content.split()
        msg = osc_message_builder.OscMessageBuilder(address = "/message")

        #Build msg for sonic pi
        #First, pitch
        try:
            toProcess = chunks[key[0]]
            if paramData[0]['isNumber'] == True:
                freq = numberPitch(toProcess, 0)
            else:
                freq = stringPitch(toProcess)
            #print(freq)
        
        except: #Assigns default if this position in the message doesn't exist.
            freq = 440
            print(bcolors.FAIL+"Pitch error, position " + str(key[0]) + " doesn't exist"+bcolors.ENDC)
            pass

        #Duration
        try:
            toProcess = chunks[key[1]]
            if paramData[1]['isNumber'] == True:
                duration = numberDuration(toProcess)
            else:
                duration = stringDuration(toProcess)
        
        except: #Assigns default if this position in the message doesn't exist.
            duration = 5
            print(bcolors.FAIL+"Dur error, position " + str(key[1]) + " doesn't exist"+bcolors.ENDC)
            pass

        #Pan
        try:
            toProcess = chunks[key[2]]
            if paramData[2]['isNumber'] == True:
                pan = numberPan(toProcess, 2)
            else:
                pan = stringPan(toProcess)
        
        except: #Assigns default if this position in the message doesn't exist.
            pan = 0
            print(bcolors.FAIL+"Pan error, position " + str(key[2]) + " doesn't exist"+bcolors.ENDC)
            pass

        msg.add_arg(freq)
        msg.add_arg(duration)
        msg.add_arg(pan)

        temp = []
        temp.append(freq)
        temp.append(duration)
        temp.append(pan)
        print(temp)
        #print("test")

        client.send(msg.build())

    except ValueError:
        msg = "ValueError: {}".format(content)
        logging.warning(msg)
        print("ValueError occured")
        raise
    except:
        print("Error occured")
        raise

def setup():
    global storagePitch
    global freqList
    global storageDuration
    global durationList
    global storagePan
    global panList
    storagePitch = []
    freqList = []
    storageDuration = []
    durationList = []
    panList = []
    storagePan = []

    initParams() #Loads in key.txt and data.txt

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

def initParams():
    global paramData
    global key

    with open('key.txt', 'r') as k:
        key = eval(k.read())

    with open('data.txt', 'r') as d:
        data = d.readlines()

    dataList = []
    for item in data:
        dataList.append(eval(item))

    paramData = []
    for item in key:
        paramData.append(dataList[item])

    print(key)
    print(paramData)
    return

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
    mqttc.subscribe('fal30') #Changed from test to wrapper.
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

def numberPitch(n, i):
    scale = [71, 69, 64, 61, 57, 52, 45, 33] #Shortest = highest

    note = "empty"
    for j in range(len(paramData[i]['bin boundaries'])):
        if n <= paramData[i]['bin boundaries'][j]:
            note = scale[j]

    if note == "empty":
        note = scale[len(paramData[i]['bin boundaries'])]
    return note

def numberDuration(n):
    '''
    if n > 0:
        duration = math.log(n)
    else:
        duration = 0
    '''
    #Do log on render.rb side
    duration = n
    return duration

def numberPan(n, i):
    if n <= paramData[i]['min']:
        pan = -1
    elif n >= paramData[i]['max']:
        pan = 1
    else:
        pan = (2*(n-paramData[i]['min'])/(paramData[i]['range']))-1
    return pan

def stringPitch(n):
    global storagePitch #Need to track objects to assign to pitches
    global freqList

    #print("Made it to stringPitch() " + str(freqList))

    if n in storagePitch:
        #print("Is in storagePitch " + str(storagePitch) + " " + str(freqList))
        freq = freqList[storagePitch.index(n)]
        #print("Set freq +")
    else:
        #print("Is not in storagePitch" + str(storagePitch) + " " + str(freqList))
        storagePitch.append(n)
        recalcTet()
        freq = freqList[storagePitch.index(n)]
        #print("Set freq -")
    return freq

def recalcTet():
    global freqList
    freqList = []

    bottom = 110 #Base of scale system in Hz
    octaves = 4 #Octave span of system
    tet = len(storagePitch)
    i = 0
    while i < tet:
        freqList.append(bottom*2**((octaves*i)/tet)) #Increments across the equally-spaced frequencies within the span of Hz.
        i+=1

    #print(freqList)
    updateLegend()
    return

def stringDuration(n):
    #print("Made it to stringDuration()")
    global storageDuration
    global durationList

    if n in storageDuration:
        duration = durationList[storageDuration.index(n)]
    else:
        storageDuration.append(n)
        recalcDur()
        duration = durationList[storageDuration.index(n)]

    return duration

def recalcDur():
    #Just do a linear spread, log it on the render.rb side as done in dj-mqtt.py
    global durationList
    durationList = []

    maxDur = 200000 #Max duration value allowed.
    step = len(storageDuration)
    i = 0
    while i < step:
        durationList.append((200000*i)/step) #Increments across the equally-spaced frequencies within the span of Hz.
        i+=1

    updateLegend()
    return

def stringPan(hashable):
    #print("Made it to stringPan()")
    global storagePan
    global panList

    if hashable not in storagePan:
        storagePan.append(hashable)

    num = hash(hashable)
    
    if num == 0:
        #print("Num is 0.")
        pan = 0
    else:
        digits = int(math.log10(abs(num)))+1
        pan = num * 10**(digits*-1)

    if pan not in panList:
        panList.append(pan)
        updateLegend()
    return pan

def updateLegend():
    global storagePitch
    global freqList
    global storageDuration
    global durationList

    with open("legend.txt", "w+") as l:
        l.writelines([
            "Legend: If lists are empty the parameter is being set by numbers in the message.\r",
            "Pitch\r",
            str(storagePitch)+'\r',
            str(freqList)+'\r',
            "Duration\r",
            str(storageDuration)+'\r',
            str(durationList)+'\r',
            "Pan\r",
            str(storagePan)+'\r',
            str(panList)+'\r'
        ])

    return

if __name__ == "__main__":
    sys.exit(main())
