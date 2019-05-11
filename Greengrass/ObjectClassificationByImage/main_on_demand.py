import sys
import timeit
import traceback
import greengrasssdk
import json
import time
import base64
import numpy as np
import cv2

import load_model

client = greengrasssdk.client('iot-data')


model_path = '/greengrass-machine-learning/mxnet/squeezenet/'
model = load_model.Model(model_path + 'synset.txt', model_path + 'squeezenet_v1.1')


def object_classification_run(input_payload):
    if model is not None:
        try:
            processing_start_time = timeit.default_timer()
            original_message = input_payload['message']
            image_string = base64.b64decode(original_message)
            predictions = model.predict_from_image(image_string)
            time.sleep(1)
            processing_end_time = timeit.default_timer()
            message = {
                'message_sent': input_payload['message_sent'],
                'processing_start_time': processing_start_time,
                'processing_end_time': processing_end_time,
                'prediction': str(predictions)
            }
            payload = json.dumps(message)
            client.publish(topic='object_classification/response', payload=payload)
        except:
            e = sys.exc_info()[0]
            print("Exception occured during prediction: %s" % e)
            exctype, value, tb = sys.exc_info()
            traceback.print_tb(tb)
    else:
        print('Model is None')


def function_handler(event, context):
    object_classification_run(event)
    # Event contains the payload
    return
