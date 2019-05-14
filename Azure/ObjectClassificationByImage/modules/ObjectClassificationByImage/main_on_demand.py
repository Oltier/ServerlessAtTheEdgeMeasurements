# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import sys
import time
import timeit
import traceback
import json
import base64
import json
import random
import time
import sys
import iothub_client
# pylint: disable=E0611
from iothub_client import IoTHubModuleClient, IoTHubClientError, IoTHubTransportProvider
from iothub_client import IoTHubMessage, IoTHubMessageDispositionResult, IoTHubError

import load_model

model_path = './squeezenet/'
model = load_model.Model(model_path + 'synset.txt', model_path + 'squeezenet_v1.1')

# messageTimeout - the maximum time in milliseconds until a message times out.
# The timeout period starts at IoTHubModuleClient.send_event_async.
# By default, messages do not expire.
MESSAGE_TIMEOUT = 10000

# global counters
RECEIVE_CALLBACKS = 0
SEND_CALLBACKS = 0
TEMPERATURE_THRESHOLD = 25
TWIN_CALLBACKS = 0

# Choose HTTP, AMQP or MQTT as transport protocol.  Currently only MQTT is supported.
PROTOCOL = IoTHubTransportProvider.MQTT


# receive_message_callback is invoked when an incoming message arrives on the specified 
# input queue (in the case of this sample, "input1").  Because this is a filter module, 
# we forward this message to the "output1" queue.
def receive_message_callback(message, hubManager):
    global RECEIVE_CALLBACKS
    global TEMPERATURE_THRESHOLD
    message_buffer = message.get_bytearray()
    message_size = len(message_buffer)
    input_payload_json = message_buffer[:message_size].decode('utf-8')
    input_payload = json.loads(input_payload_json)
    print(input_payload)
    response_payload = object_classification_run(input_payload)
    print(response_payload)
    # hub_manager.respond(response_payload)
    return IoTHubMessageDispositionResult.ACCEPTED


def object_classification_run(input_payload):
    if model is not None:
        try:
            processing_start_time = timeit.default_timer()
            original_message = input_payload['message']
            image_string = base64.b64decode(original_message)
            predictions = model.predict_from_image(image_string)
            processing_end_time = timeit.default_timer()
            message = {
                'message_sent': input_payload['message_sent'],
                'processing_start_time': processing_start_time,
                'processing_end_time': processing_end_time,
                'prediction': str(predictions)
            }
            print(message)
            return json.dumps(message)
        except Exception as ex:
            e = sys.exc_info()[0]
            print("Exception occured during prediction: %s" % e)
            print("Exception occured: {}".format(ex))
            exctype, value, tb = sys.exc_info()
            traceback.print_tb(tb)
    else:
        print('Model is None')


class HubManager(object):

    def __init__(
            self,
            protocol=IoTHubTransportProvider.MQTT):
        self.client_protocol = protocol
        self.client = IoTHubModuleClient()
        self.client.create_from_environment(protocol)

        # set the time until a message times out
        self.client.set_option("messageTimeout", MESSAGE_TIMEOUT)

        # sets the callback when a message arrives on "input1" queue.  Messages sent to 
        # other inputs or to the default will be silently discarded.
        self.client.set_message_callback("input1", receive_message_callback, self)


def main(protocol):
    try:
        print ("\nPython %s\n" % sys.version)
        print ("IoT Hub Client for Python")

        hub_manager = HubManager(protocol)

        print ("Starting the IoT Hub Python sample using protocol %s..." % hub_manager.client_protocol)
        print ("The sample is now waiting for messages and will indefinitely.  Press Ctrl-C to exit. ")

        while True:
            time.sleep(1)

    except IoTHubError as iothub_error:
        print ("Unexpected error %s from IoTHub" % iothub_error)
        return
    except KeyboardInterrupt:
        print ("IoTHubModuleClient sample stopped")


if __name__ == '__main__':
    main(PROTOCOL)
