import paho.mqtt.client as mqtt

"""
Subscribe to mqtt 'test' topic
"""

PORT=1883
HOST='py-dev.lancs.ac.uk'

def on_message(mosq, userdata, msg):
    content = msg.payload.decode("utf-8")#.rstrip()[:140]
    print(content.split())

def mqttHandler():
    mqttc.connect(HOST, PORT)
    mqttc.subscribe('fal30')
    while True:
        mqttc.loop()

if __name__ == '__main__':
    mqttc = mqtt.Client()
    mqttc.on_message = on_message
    mqttHandler()
