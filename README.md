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
such plots. This project attempts to use sonification to add an audiable
component.

### Why?

An audio stream is less intrusive if done correctly. A common pattern when
using audio is with alerts. ie. play a loud annoying sound when a bad thing
happens. eg. LHC beam dump (toilet flush) and eg. LIGOS beam lock lost ([train
whistle](https://vimeo.com/122982348)).

Also, ambient sounds can be subtle and useful ([ask the captain](https://vimeo.com/122996114))

### How?

The following components are currently being used:

* logstash (collection)
* zeromq (messaging)
* python (orchestration and translation of messages)
* Renoise (synth engine)

A sound rendering engine is required and currently the commercial (and awesome)
application used is called [Renoise](http://www.renoise.com). A suitable Opensource
solution would be something like
[Supercollider](http://supercollider.sourceforge.net/). Most synth engines will
accept Open Sound Control messages as output by the python orchestration
script. To do this we need the pyOSC client library and also pyzmq bindings.
Install via pip:

```
$ pip install pyOSC
$ pip install pyzmq
```

### Run it

1. run logstash and output zeromq messages [module](http://logstash.net/docs/latest/outputs/zeromq)
2. use the ./fwdr.py script to setup a zeromq forwarder
3. consume messages using the dj.py script
  1. See help options `./dj.py -h`
4. start Renoise change OSC preferences to 'Enable Server'
5. play with dj.py options and send OSC to Renoise
