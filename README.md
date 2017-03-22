# IoToDb
Raspberry Pi to Cassandra

Sensor with Arduino with XBee (Tx) --- (Rx) Xbee with Raspberry Pi Gateway --- 
                                            ---> Publish (MQTT Broker/Azure IoT Hub) 
                                              --- MQTT Broker <--- Subscribe to IoT Hub from sever host/center (Dashboard / App) 
                                              --- MQTT Broker --------------> Push to Cloud DB

Sensor1 ... Sensor10 => Raspberry Pi Gateway

Sensor10 ... Sensor20 => Raspberry Pi Gateway

Sensor20 ... Sensor30 => Raspberry Pi Gateway

...



