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

def dictCheck(pos, chunks):
    global storeDicts
    if chunks[pos] in storeDicts[pos]:
            storeDicts[pos][chunks[pos]] += 1
    else:
        storeDicts[pos][chunks[pos]] = 1
    return

def update(chunks):
    global storeDicts
    if len(storeDicts) < len(chunks):
        for i in range(len(storeDicts)):
            dictCheck(i, chunks)
        j = len(storeDicts)
        while j < len(chunks):
            storeDicts.append({chunks[j]: 1})
            j += 1

    else:
        for i in range(len(chunks)):
            dictCheck(i, chunks)

    '''
    f= open("dicts.txt","w+")
    for item in storeDicts:
        f.write(str(item) + '\r')
    f.close()
    '''

def on_message(mosq, userdata, msg):
    content = msg.payload.decode("utf-8").rstrip()[:140]

    try:    
        update(content.split())

        if 'fault' in content:
            print(bcolors.FAIL+content+bcolors.ENDC)
        else:
            print(content)

    except ValueError:
        msg = "ValueError: {}".format(content)
        logging.warning(msg)
        raise
    except:
        raise

def main():
    global storeDicts
    storeDicts = []

    mqttc = mqtt.Client()
    mqttc.connect(HOST, PORT)
    mqttc.subscribe('wrapper') #Changed from test to wrapper.
    mqttc.on_message = on_message
    while True:
        mqttc.loop()

        try:
            #To exit program gracefully
            if keyboard.is_pressed('ctrl+shift+x'):
                print(bcolors.OKGREEN+"Exited mqttc loop."+bcolors.ENDC)
                break
        except:
            pass

    f= open("dicts.txt","w+")
    for item in storeDicts:
        f.write(str(item) + '\r')
    f.close()

    print("Analysing data.")

    analyse()

    g= open("data.txt","w+")
    for item in storeData:
        g.write(str(item) + '\r')
    g.close()

    print("End of program.")

def analyse():
    global storeData
    storeData = []
    #First need to check if the dict in question is pure number or not.
    for dictionary in storeDicts:
        isNumber = True
        for key in dictionary:
            try:
                float(key)
            except ValueError:
                isNumber = False
                break
        storeData.append({"isNumber": isNumber})

    #print(storeData)
    #Then need to act on the dicts accordingly.
    for i in range(len(storeData)):
        if storeData[i]["isNumber"]:
            numProcess(i)
        else:
            strProcess(i)
    return

def numProcess(pos):
    numList = []
    for item in list(storeDicts[pos]):
        try:
            toAppend = int(item)
            print("Made int")
        except ValueError:
            toAppend = float(item)
            print("Made float")
        numList.append(toAppend)
    numList.sort()
    #print(numList)
    storeData[pos]["min"] = float(numList[0])
    storeData[pos]["max"] = float(numList[-1])
    storeData[pos]["range"] = (float(numList[-1]) - float(numList[0]))
    return

def strProcess(pos):
    strList = []
    strList = list(storeDicts[pos])
    #Now work out total frequency of the contents.
    totalf = 0
    for i in range(len(strList)):
        totalf += storeDicts[pos][strList[i]]

    rating = totalf / len(strList)
    storeData[pos]["num items"] = len(strList)
    storeData[pos]["rating"] = rating

if __name__ == "__main__":
    sys.exit(main())
