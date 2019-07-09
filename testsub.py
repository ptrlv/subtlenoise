import paho.mqtt.client as mqtt

"""
Subscribe to mqtt 'test' topic
"""

PORT=1883
HOST='py-dev.lancs.ac.uk'

def on_message(mosq, userdata, msg):
    print("Got topic: " + msg.topic + ", message: " + msg.payload.decode("utf-8"))

def mqttHandler():
    mqttc.connect(HOST, PORT)
    mqttc.subscribe('test')
    while True:
        mqttc.loop()

if __name__ == '__main__':
    mqttc = mqtt.Client()
    mqttc.on_message = on_message
    mqttHandler()
