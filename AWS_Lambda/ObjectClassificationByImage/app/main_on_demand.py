import timeit
import json
import base64
import boto3

import load_model

client = boto3.client('iot-data')

model_path = './squeezenet/'
model = load_model.Model(model_path + 'synset.txt', model_path + 'squeezenet_v1.1')


def object_classification_run(input_payload):
    if model is not None:
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
        return payload
    else:
        print('Model is None')


def function_handler(event, context):
    response_payload = object_classification_run(event)
    client.publish(topic='object_classification/response', payload=response_payload)
    print("Published")
    return
