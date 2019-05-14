import sys
import time
import timeit
import traceback
import json
import base64
import iothub_client
# pylint: disable=E0611
from iothub_client import IoTHubModuleClient, IoTHubClientError, IoTHubTransportProvider
from iothub_client import IoTHubMessage, IoTHubMessageDispositionResult, IoTHubError

import load_model

model_path = './squeezenet/'
model = load_model.Model(model_path + 'synset.txt', model_path + 'squeezenet_v1.1')

MESSAGE_TIMEOUT = 10000
OUTPUT_QUEUE_NAME = 'object_classification/response'
INPUT_QUEUE_NAME = 'object_classification/request'


def receive_message_callback(message, hub_manager):
    message_buffer = message.get_bytearray()
    message_size = len(message_buffer)
    input_payload_json = message_buffer[:message_size].decode('utf-8')
    input_payload = json.loads(input_payload_json)
    print(input_payload)
    #eper
    # response_payload = object_classification_run(input_payload)
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

    def __init__(self):
        protocol = IoTHubTransportProvider.MQTT
        self.client_protocol = protocol
        self.client = IoTHubModuleClient()
        self.client.create_from_environment(protocol)

        # set the time until a message times out
        self.client.set_option("messageTimeout", MESSAGE_TIMEOUT)

        # sets the callback when a message arrives on "input1" queue.  Messages sent to
        # other inputs or to the default will be silently discarded.
        self.client.set_message_callback(INPUT_QUEUE_NAME, receive_message_callback, self)

    def respond(self, response_payload):
        self.client.send_event_async(OUTPUT_QUEUE_NAME, response_payload, None, None)


def main():
    try:
        hub_manager = HubManager()

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
    main()
