import sys
import timeit
import traceback
import json
import base64

import load_model


model_path = '/greengrass-machine-learning/mxnet/squeezenet/'
model = load_model.Model(model_path + 'synset.txt', model_path + 'squeezenet_v1.1')


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
            payload = json.dumps(message)
            # TODO response
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
