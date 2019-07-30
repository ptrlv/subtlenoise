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

import numpy as np
import matplotlib.pyplot as plt
#import matplotlib.animation as animation
import matplotlib.patches as patches
import matplotlib.path as path


PORT=1883
HOST='148.88.67.14'

#Generates axes and window to be updated.
def init(var=[]):
    global xdata, fig, ax, patch

    #xdata = var
    xdata = [1, 2, 3, 4, 5, 6, 7, 8]

    fig, ax = plt.subplots()
    plt.ion()
    plt.show()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)

    n, bins = np.histogram(xdata, 'auto')

    # get the corners of the rectangles for the histogram
    left = np.array(bins[:-1])
    right = np.array(bins[1:])
    bottom = np.zeros(len(left))
    top = bottom + n


    # we need a (numrects x numsides x 2) numpy array for the path helper
    # function to build a compound path
    XY = np.array([[left, left, right, right], [bottom, top, top, bottom]]).T

    # get the Path object
    barpath = path.Path.make_compound_path_from_polys(XY)

    # make a patch out of it
    patch = patches.PathPatch(barpath)
    ax.add_patch(patch)

#Updates graph to histogram of most recent data.
def update(x):
	global xdata, patch
	patch.remove()
	xdata.append(x)

	n, bins = np.histogram(xdata, 8) #'auto')

	# get the corners of the rectangles for the histogram
	left = np.array(bins[:-1])
	right = np.array(bins[1:])
	bottom = np.zeros(len(left))
	top = bottom + n


	# we need a (numrects x numsides x 2) numpy array for the path helper
	# function to build a compound path
	XY = np.array([[left, left, right, right], [bottom, top, top, bottom]]).T

	# get the Path object
	barpath = path.Path.make_compound_path_from_polys(XY)

	# make a patch out of it
	patch = patches.PathPatch(barpath)
	ax.add_patch(patch)

	# update the view limits
	ax.set_xlim(left[0], right[-1])
	ax.set_ylim(bottom.min(), top.max())

	#Have to trigger pause to update frame must be non-zero
	plt.pause(np.exp(-17))

def on_message(mosq, userdata, msg):
    global args
    global client
    #global duration

    #global isPrinting #Checks whether input stream should be paused.

    content = msg.payload.decode("utf-8").rstrip()[:140]
    try:
        #if isPrinting:
        if 'exiting' in content: #duration = int(content.split()[1])
            duration = int(content.split()[1])
            print(str(duration) + "\t" + str(math.log(duration)))
            if duration != 0:
                #update(math.log(duration)) #Graphing log of duration to get a better distribution of results.

                #Just to check population of bins for equal note distribution also changed xdata to get correct bin placement.

                logTime = math.log(duration)

                if logTime <= 4.0:
                    update(1)
                elif 4.0 <= logTime <= 5.0:
                    update(2)
                elif 5.0 <= logTime <= 6.0:
                    update(3)
                elif 6.0 <= logTime <= 7.0:
                    update(4)
                elif 7.0 <= logTime <= 8.0:
                    update(5)
                elif 8.0 <= logTime <= 9.0:
                    update(6)
                elif 9.0 <= logTime <= 10.0:
                    update(7)
                elif 10.0 <= logTime:
                    update(8)

        else:
            duration = 0
            #print(duration)

    except ValueError:
        msg = "ValueError: {}".format(content)
        logging.warning(msg)
    except:
        raise

def main():
    global client
    init()
    #global duration

    #Checks whether input stream should be paused.
    #global isPrinting
    #isPrinting = True

    mqttc = mqtt.Client()
    mqttc.connect(HOST, PORT)
    mqttc.subscribe('test')
    mqttc.on_message = on_message

    while True:
        mqttc.loop()
    input("Press [enter] to continue.")

if __name__ == "__main__":
    sys.exit(main())