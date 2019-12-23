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
import statistics

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

#Checks if part of message being looked at has been seen before and counts it.
def dictCheck(pos, chunks):
    global storeDicts
    if chunks[pos] in storeDicts[pos]:
            storeDicts[pos][chunks[pos]] += 1
    else:
        storeDicts[pos][chunks[pos]] = 1
    return

#Checks each part of the received message to see if a dictionary exists for that chunk and calls dictCheck().
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

#Splits the received message into chunks and calls update() on the list of chunks.
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

#Runs message receive loop and exits to start analysis when user inputs "ctrl+shift+X".
def main():
    global storeDicts
    storeDicts = []

    mqttc = mqtt.Client()
    mqttc.connect(HOST, PORT)
    mqttc.subscribe('fal30') #Changed from test to wrapper.
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

    print("Trimming data")

    trim()

    f= open("dictsTrimmed.txt","w+")
    for item in storeDicts:
        f.write(str(item) + '\r')
    f.close()

    print("Analysing trimmed data.")

    analyse()

    g= open("dataTrimmed.txt","w+")
    for item in storeData:
        g.write(str(item) + '\r')
    g.close()

    print("End of program.")

#Checks whether each dictionary of received message chunks is purely numerical.
#Sends dictionary to relevant numProcess() or strProcess() depending on result.
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

#Processes purely numerical dictionaries to get useful data for sound creation.
def numProcess(pos):
    numList = []
    for item in list(storeDicts[pos]):
        try:
            toAppend = int(item)
            #print("Made int")
        except ValueError:
            toAppend = float(item)
            #print("Made float")
        numList.append(toAppend)
    numList.sort()
    #print(numList)
    if len(numList) > 0:
        storeData[pos]["min"] = float(numList[0])
        storeData[pos]["max"] = float(numList[-1])
        storeData[pos]["range"] = (float(numList[-1]) - float(numList[0]))
    else:
        storeData[pos]["min"] = "N/A"
        storeData[pos]["max"] = "N/A"
        storeData[pos]["range"] = "N/A"

    cutPoints = binData(pos, numList)
    storeData[pos]["bin boundaries"] = cutPoints
    return

#Processes other dictionaries to rate them for importance wrt sonification.
def strProcess(pos):
    strList = []
    strList = list(storeDicts[pos])
    #Now work out total frequency of the contents.
    totalf = 0
    for i in range(len(strList)):
        totalf += storeDicts[pos][strList[i]]

    #Calculates rating of how strong patterns are in the data.
    if len(strList) > 1:
        rating = totalf / len(strList)
    else:
        rating = 0 #Rates as not useful chunks which always have the same value.

    storeData[pos]["num items"] = len(strList)
    storeData[pos]["rating"] = rating

#Takes a range of numbers and bins them into useful subgroups for mapping to 8 musical notes.
def binData(pos, numList):
    #Need to generate full list of every value received.
    fullList = []
    for item in numList:
        i = 0
        while i < storeDicts[pos][str(item)]:
            fullList.append(item)
            i+=1

    #print(statistics.quantiles(fullList, n=8, method='exclusive'))
    #cutList = statistics.quantiles(fullList, n=8, method='inclusive')
    cutList = []

    #More useful binning, accounts for spikes in frequency of one result.
    #Needs to iterate across all the cuts.
    if len(list(storeDicts[pos])) > 8:
        i = 8
    else:
        i = len(list(storeDicts[pos]))-1
    #print("i value is" + str(i))
    #print("fullList is" + str(fullList))

    while i > 1:
        val = statistics.quantiles(fullList, n=i, method='exclusive')[0]
        cutList.append(val)
        while fullList[0] <= val:
            fullList.pop(0)
        i -= 1

    #print(cutList)
    return cutList

#Removes keys with values that are the same as values in earlier chunks.
def trim():
    for i in range(len(storeDicts)): #Iterating through each chunk from start to finish.
        if storeData[i]["isNumber"] == False:
            for entry in list(storeDicts[i]): #Iterates through each key in the dict.
                val = storeDicts[i][entry] #Stores value to be compared against.
                if val > 1:
                    j = i + 1
                    while j < len(storeDicts): #Iterates across all chunks after the present one.
                        if storeData[j]["isNumber"] == False:
                            for item in list(storeDicts[j]): #Iterates through the dict, checking for matches.
                                if storeDicts[j][item] == val:
                                    storeDicts[j].pop(item)
                                    break #Removes matching key and breaks loop
                        j += 1
    return

if __name__ == "__main__":
    sys.exit(main())
