# -*- coding: utf-8 -*-
import sys
import paho.mqtt.client as mqtt
import Adafruit_DHT

# Parse command line parameters.
sensor_args = { '11': Adafruit_DHT.DHT11,
                '22': Adafruit_DHT.DHT22,
                '2302': Adafruit_DHT.AM2302 }
if len(sys.argv) == 3 and sys.argv[1] in sensor_args:
    sensor = sensor_args[sys.argv[1]]
    pin = sys.argv[2]
else:
    print('usage: sudo ./Adafruit_DHT_MQTT.py [11|22|2302] GPIOpin#')
    print('example: sudo ./Adafruit_DHT_MQTT.py 2302 4 - Read from an AM2302 connected to GPIO #4')
    sys.exit(1)

# Try to grab a sensor reading.  Use the read_retry method which will retry up
# to 15 times to get a sensor reading (waiting 2 seconds between each retry).
humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

# Un-comment the line below to convert the temperature to Fahrenheit.
# temperature = temperature * 9/5.0 + 3

print('Main: Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity))

sensor_msg = "SensorMsg: Temp={0:0.1f}*  Humidity={1:0.1f}%".format(temperature, humidity)


mqttc = mqtt.Client("python_pub")
mqttc.connect("192.168.1.119", 1883)
mqttc.publish("sensor/data", sensor_msg)
mqttc.loop(2)
