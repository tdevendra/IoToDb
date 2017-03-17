import sys

import Adafruit_DHT
from cassandra.cluster import Cluster

# Parse command line parameters.
sensor_args = { '11': Adafruit_DHT.DHT11,
                '22': Adafruit_DHT.DHT22,
                '2302': Adafruit_DHT.AM2302 }
if len(sys.argv) == 3 and sys.argv[1] in sensor_args:
    sensor = sensor_args[sys.argv[1]]
    pin = sys.argv[2]
else:
    print('usage: sudo ./Adafruit_DHT.py [11|22|2302] GPIOpin#')
    print('example: sudo ./Adafruit_DHT.py 2302 4 - Read from an AM2302 connected to GPIO #4')
    sys.exit(1)

# Try to grab a sensor reading.  Use the read_retry method which will retry up
# to 15 times to get a sensor reading (waiting 2 seconds between each retry).
humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

cluster = Cluster()
session = cluster.connect()

session.set_keyspace('demo')

p = session.prepare("""
    INSERT INTO temphum(id, temp, humidity)
    VALUES(?, ?, ?)
    """)

# temperature = temperature * 9/5.0 + 32

# Note that sometimes you won't get a reading and
# the results will be null (because Linux can't
# guarantee the timing of calls to read the sensor).
# If this happens try again!
if humidity is not None and temperature is not None:
    print("Raw Temp={0} Humidity={1}".format(temperature, humidity))
    print('Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity))
    session.execute(p, (3, temperature, humidity))
else:
    print('Failed to get reading. Try again!')
    sys.exit(1)

print("Fetching values...")
future = session.execute_async("SELECT * FROM temphum")

rows = future.result()

for row in rows:
    print "".join(str(row))


