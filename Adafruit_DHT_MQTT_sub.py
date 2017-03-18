import time
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import sys


Broker = "192.168.1.119"
#sub_topic = "sensor/instructions"    # receive messages on this topic
pub_topic = "sensor/data"       # send messages to this topic

############### MQTT section ##################

# when connecting to mqtt do this
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(pub_topic)

# when receiving a mqtt message do this
def on_message(client, userdata, msg):
    message = str(msg.payload)
    print("Topic: ", msg.topic + "\n Message: " + message)

def on_publish(mosq, obj, mid):
    print("mid: " + str(mid))


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(Broker, 1883, 60)
client.loop_forever()
