import sys
import datetime
import traceback
import greengrasssdk

import load_model

client = greengrasssdk.client('iot-data')


# model_path = '/greengrass-machine-learning/mxnet/squeezenet/'
# model = load_model.Model(model_path + 'synset.txt', model_path + 'squeezenet_v1.1')


def object_classification_run(image):
    # if model is not None:
    try:
        # predictions = model.predict_from_image(image)
        # payload = 'Prediction: {}'.format(str(predictions))
        client.publish(topic='object_classification/response', payload='Hello lambda!')
    except:
        e = sys.exc_info()[0]
        print("Exception occured during prediction: %s" % e)
        exctype, value, tb = sys.exc_info()
        traceback.print_tb(tb)


def function_handler(event, context):
    object_classification_run('')
    # Event contains the payload
    print(event)
    return
