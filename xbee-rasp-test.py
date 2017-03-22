import serial

ser = serial.Serial('/dev/serial0', 9600)

while 1:
    print ser.read()

