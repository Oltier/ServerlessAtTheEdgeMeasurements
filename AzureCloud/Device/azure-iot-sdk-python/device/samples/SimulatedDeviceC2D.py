import time
import sys
import iothub_client
from iothub_client import IoTHubClient, IoTHubClientError, IoTHubTransportProvider, IoTHubClientResult
from iothub_client import IoTHubMessage, IoTHubMessageDispositionResult, IoTHubError

RECEIVE_CONTEXT = 0
WAIT_COUNT = 10
RECEIVED_COUNT = 0
RECEIVE_CALLBACKS = 0

# choose AMQP or AMQP_WS as transport protocol
PROTOCOL = IoTHubTransportProvider.AMQP
CONNECTION_STRING = "HostName=AzureFunctionsHub.azure-devices.net;DeviceId=AzureFunctionsDevice;SharedAccessKey" \
                    "=KFABId+taVMssEexHmK4gd1XZCCFMKQvjk2DcHyVHlc= "


def receive_message_callback(message, counter):
    global RECEIVE_CALLBACKS
    message_buffer = message.get_bytearray()
    size = len(message_buffer)
    print ("Received Message [%d]:" % counter)
    print ("    Data: <<<%s>>> & Size=%d" % (message_buffer[:size].decode('utf-8'), size))
    map_properties = message.properties()
    key_value_pair = map_properties.get_internals()
    print ("    Properties: %s" % key_value_pair)
    counter += 1
    RECEIVE_CALLBACKS += 1
    print ("    Total calls received: %d" % RECEIVE_CALLBACKS)
    return IoTHubMessageDispositionResult.ACCEPTED


def iothub_client_init():
    client = IoTHubClient(CONNECTION_STRING, PROTOCOL)

    client.set_message_callback(receive_message_callback, RECEIVE_CONTEXT)

    return client


def print_last_message_time(client):
    try:
        last_message = client.get_last_message_receive_time()
        print ("Last Message: %s" % time.asctime(time.localtime(last_message)))
        print ("Actual time : %s" % time.asctime())
    except IoTHubClientError as iothub_client_error:
        if iothub_client_error.args[0].result == IoTHubClientResult.INDEFINITE_TIME:
            print ("No message received")
        else:
            print (iothub_client_error)


def iothub_client_sample_run():
    try:
        client = iothub_client_init()

        while True:
            print ("IoTHubClient waiting for commands, press Ctrl-C to exit")

            status_counter = 0
            while status_counter <= WAIT_COUNT:
                status = client.get_send_status()
                print ("Send status: %s" % status)
                time.sleep(10)
                status_counter += 1

    except IoTHubError as iothub_error:
        print ("Unexpected error %s from IoTHub" % iothub_error)
        return
    except KeyboardInterrupt:
        print ("IoTHubClient sample stopped")

    print_last_message_time(client)


if __name__ == '__main__':
    print ("Starting the IoT Hub Python sample...")
    print ("    Protocol %s" % PROTOCOL)
    print ("    Connection string=%s" % CONNECTION_STRING)

    iothub_client_sample_run()
