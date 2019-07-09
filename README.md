# subtlenoise

Subtlenoise produces low-impact but information-rich soundscapes in realtime.
The intended usecase is to monitor distributed computing operations and
supplement the traditional monitoring services such as dashboards.

The implementation is described below but is flexible in terms of the various
components which may be used. Subtlenoise is more of an architecture than a
complete software solution. At the heart of the system is a python script used
to sonify incoming messages and output messages suitable for audio-rendering.

### What?

We want monitoring to be less intrusive. The well-known pattern of time-series
histogram is visually rich but also visually overwhelming when digesting many
such plots. This project attempts to use sonification to provide an [Auditory
display.](http://en.wikipedia.org/wiki/Auditory_display)

### Why?

An audio stream is less intrusive if done correctly (and horribly annoying if
done poorly). Ultimately we want a situation where the ambient sounds can be
useful and totally unobstrusive ([Picard knows](https://vimeo.com/122118684))

The human brain is adept at extracting information from subtle environmental
noise ([Paul knows](https://vimeo.com/122996114))

### How?

The following components are being used to collect, transport, translate, and
emit messages in the Subtlenoise pipeline:

* UDP (collection)
* mqtt (messaging)
* python (orchestration and translation of messages)
* SonicPI (audio rendering)

Opensource sound rendering tool is [SonicPi](https://sonic-pi.net/) which uses
[Supercollider](http://supercollider.sourceforge.net/) under the hood.  Most
synth engines will accept Open Sound Control (OSC) messages as output by the
python orchestration script. To do this we need the python-osc and mqtt
packages. Install via pip:

```
$ pip install paho-mqtt
$ pip install python-osc
```

### Run it

1. use dj-mqtt.py to subscribe to the mqtt message stream
2. consume messages using the dj-mqtt.py script
3. start Sonic Pi and ensure the OSC server is running
5. experiment with Sonic Pi ruby code (example is render.rb)


### Comments

1. The abscence of signal is informative

2. A common pattern is to use audio cues when certain events occur, clumsily
called [Earcons](http://en.wikipedia.org/wiki/Earcon). For example, the train
whistle when the LIGOS experiment loses beam lock ([Earcon
example](https://vimeo.com/122982348)).

3. Needs to be unobtrusive otherwise it becomes very annoying very quickly

4. Monitorrama talk from Joe Ruscio with some toptips for visualisation
[http://vimeo.com/62630749](http://vimeo.com/62630749)

5. Nice description of how to process incoming data
[thelisteningmachine](http://www.thelisteningmachine.org/about)

6. pertinent comment "...more than just white noise. It is a richly layered
audio experience, with enough variation to prevent monotony but not so variable
as to become distracting (which ambient sound should never be)” -
[http://www.youtube.com/watch?v=icFT76pHgoM](youtube)

### this is not

1. NOT entertainment  [BBC sounds of space](http://www.bbc.co.uk/programmes/b050bwpp)
2. NOT musical  [LHCchamber music](https://www.youtube.com/watch?v=gPmQcviT-R4)
3. NOT a curiosity [LHC sound](http://lhcsound.hep.ucl.ac.uk/)

The above are good examples of outreach and inspirational news items, but are not the sonification we’re looking for...
