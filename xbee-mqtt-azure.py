import serial
import sys
import paho.mqtt.client as mqtt

import iothub_client
from iothub_client import IoTHubClient, IoTHubClientError, IoTHubTransportProvider, IoTHubClientResult
from iothub_client import IoTHubMessage, IoTHubMessageDispositionResult, IoTHubError, DeviceMethodReturnValue
from iothub_client_args import get_iothub_opt, OptionError

# chose HTTP, AMQP or MQTT as transport protocol
PROTOCOL = IoTHubTransportProvider.MQTT

# String containing Hostname, Device Id & Device Key in the format:
# "HostName=<host_name>;DeviceId=<device_id>;SharedAccessKey=<device_key>"
CONNECTION_STRING = "[Device Connection String]"
MESSAGE_TIMEOUT = 5

RECEIVE_CONTEXT = 0
AVG_WIND_SPEED = 10.0
MESSAGE_COUNT = 5
RECEIVED_COUNT = 0
TWIN_CONTEXT = 0
SEND_REPORTED_STATE_CONTEXT = 0
METHOD_CONTEXT = 0

# global counters
RECEIVE_CALLBACKS = 0
SEND_CALLBACKS = 0
BLOB_CALLBACKS = 0
TWIN_CALLBACKS = 0
SEND_REPORTED_STATE_CALLBACKS = 0
METHOD_CALLBACKS = 0

def set_certificates(client):
    from iothub_client_cert import CERTIFICATES
    try:
        client.set_option("TrustedCerts", CERTIFICATES)
        print ( "set_option TrustedCerts successful" )
    except IoTHubClientError as iothub_client_error:
        print ( "set_option TrustedCerts failed (%s)" % iothub_client_error )

def send_confirmation_callback(message, result, user_context):
    global SEND_CALLBACKS
    message_buffer = message.get_bytearray()
    size = len(message_buffer)
    messagePayload = message_buffer.decode('utf-8')
    print ( "   data: <<<{0}>>> & Size={1}".format(messagePayload, size) )
    print ( "Confirmation[%d] received for message with result = %s" % (user_context, result) )
    map_properties = message.properties()
    print ( "    message_id: %s" % message.message_id )
    print ( "    correlation_id: %s" % message.correlation_id )
    key_value_pair = map_properties.get_internals()
    print ( "    Properties: %s" % key_value_pair )
    SEND_CALLBACKS += 1
    print ( "    Total calls confirmed: %d" % SEND_CALLBACKS )

def device_twin_callback(update_state, payload, user_context):
    global TWIN_CALLBACKS
    print ( "\nTwin callback called with:\nupdateStatus = %s\npayload = %s\ncontext = %s" % (update_state, payload, user_context) )
    TWIN_CALLBACKS += 1
    print ( "Total calls confirmed: %d\n" % TWIN_CALLBACKS )

def send_reported_state_callback(status_code, user_context):
    global SEND_REPORTED_STATE_CALLBACKS
    print ( "Confirmation for reported state received with:\nstatus_code = [%d]\ncontext = %s" % (status_code, user_context) )
    SEND_REPORTED_STATE_CALLBACKS += 1
    print ( "    Total calls confirmed: %d" % SEND_REPORTED_STATE_CALLBACKS )

def receive_message_callback(message, counter):
    global RECEIVE_CALLBACKS
    message_buffer = message.get_bytearray()
    size = len(message_buffer)
    print ( "Received Message [%d]:" % counter )
    print ( "    Data: <<<%s>>> & Size=%d" % (message_buffer[:size].decode('utf-8'), size) )
    map_properties = message.properties()
    key_value_pair = map_properties.get_internals()
    print ( "    Properties: %s" % key_value_pair )
    counter += 1
    RECEIVE_CALLBACKS += 1
    print ( "    Total calls received: %d" % RECEIVE_CALLBACKS )
    return IoTHubMessageDispositionResult.ACCEPTED

def device_method_callback(method_name, payload, user_context):
    global METHOD_CALLBACKS
    print ( "\nMethod callback called with:\nmethodName = %s\npayload = %s\ncontext = %s" % (method_name, payload, user_context) )
    METHOD_CALLBACKS += 1
    print ( "Total calls confirmed: %d\n" % METHOD_CALLBACKS )
    device_method_return_value = DeviceMethodReturnValue()
    device_method_return_value.response = "{ \"Response\": \"This is the response from the device\" }"
    device_method_return_value.status = 200
    return device_method_return_value

def blob_upload_conf_callback(result, user_context):
    global BLOB_CALLBACKS
    print ( "Blob upload confirmation[%d] received for message with result = %s" % (user_context, result) )
    BLOB_CALLBACKS += 1
    print ( "    Total calls confirmed: %d" % BLOB_CALLBACKS )

def iothub_client_init():
    # Prepare iothub client
    client = IoTHubClient(CONNECTION_STRING, PROTOCOL)

    # Set the time until a message times out
    client.set_option("messageTimeout", MESSAGE_TIMEOUT)

    # Some embedded platforms need certificate information
    set_certificates(client)

    return client

def print_last_message_time(client):
    try:
        last_message = client.get_last_message_receive_time()
        print ( "Last Message: %s" % time.asctime(time.localtime(last_message)) )
        print ( "Actual time : %s" % time.asctime() )
    except IoTHubClientError as iothub_client_error:
        if iothub_client_error.args[0].result == IoTHubClientResult.INDEFINITE_TIME:
            print ( "No message received" )
        else:
            print ( iothub_client_error )

def iothub_client_sample_run():
    """
    IoT Hub Sample execution
    """
    try:
        client = iothub_client_init()

        if client.protocol == IoTHubTransportProvider.MQTT:
            print ( "IoTHubClient is reporting state" )
            reported_state = "{\"newState\":\"standBy\"}"
            client.send_reported_state(reported_state, len(reported_state), send_reported_state_callback, SEND_REPORTED_STATE_CONTEXT)

        while True:
            # send a few messages every minute
            print ( "IoTHubClient sending %d messages" % MESSAGE_COUNT )

            for message_counter in range(0, MESSAGE_COUNT):
                # msg_txt_formatted = "To IoT Hub From XBee"
                ser = serial.Serial('/dev/serial0', 9600)
                msg_txt_formatted = ser.read()
                message = IoTHubMessage(bytearray(msg_txt_formatted, 'utf8'))

                message.message_id = "message_%d" % message_counter
                message.correlation_id = "correlation_%d" % message_counter

                # optional: assign properties
                prop_map = message.properties()
                prop_text = "PropMsg_%d" % message_counter
                prop_map.add("Property", prop_text)

                client.send_event_async(message, send_confirmation_callback, message_counter)
    except IoTHubError as iothub_error:
        print ( "Unexpected error %s from IoTHub" % iothub_error )
        return
    except KeyboardInterrupt:
        print ( "IoTHubClient sample stopped" )

    print_last_message_time(client)

def usage():
    print ( "Usage: iothub_client_sample.py -p <protocol> -c <connectionstring>" )
    print ( "    protocol        : <amqp, amqp_ws, http, mqtt, mqtt_ws>" )
    print ( "    connectionstring: <HostName=<host_name>;DeviceId=<device_id>;SharedAccessKey=<device_key>>" )


if __name__ == '__main__':
    print ( "\nPython %s" % sys.version )
    print ( "IoT Hub for Python SDK Version: %s" % iothub_client.__version__ )

    try:
        (CONNECTION_STRING, PROTOCOL) = get_iothub_opt(sys.argv[1:], CONNECTION_STRING, PROTOCOL)
    except OptionError as option_error:
        print ( option_error )
        usage()
        sys.exit(1)

    print ( "Starting the IoT Hub Python sample..." )
    print ( "    Protocol %s" % PROTOCOL )
    print ( "    Connection string=%s" % CONNECTION_STRING )

    iothub_client_sample_run()

#ser = serial.Serial('/dev/serial0', 9600)

#print ser.read()

#mqttc = mqtt.Client("python_pub")
#mqttc.connect("192.168.1.119", 1883)

# Read Data from Sensor using XBee and
# write data to MQTT 
# MQTT bridge to Azure IoT Hub
# Azure IoT Hub to Cassandra DB

#while 1:
#    print ser.read()
#    sensor_msg = "Test Msg"
#    mqttc.publish("sensor/data", sensor_msg)

#mqttc.loop(2)
