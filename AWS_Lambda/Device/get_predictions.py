# /*
# * Copyright 2010-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# *
# * Licensed under the Apache License, Version 2.0 (the "License").
# * You may not use this file except in compliance with the License.
# * A copy of the License is located at
# *
# *  http://aws.amazon.com/apache2.0
# *
# * or in the "license" file accompanying this file. This file is distributed
# * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# * express or implied. See the License for the specific language governing
# * permissions and limitations under the License.
# */


import sys
import time
import json
import logging
import base64
import timeit
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

stats = open('stats.csv', 'a+')
stats.write("message_sent,processing_start_time,processing_end_time,message_arrived,network_delay,processing_delay,"
            "overall_delay\n")


# General message notification callback
def customOnMessage(client, userdata, message):
    message_arrived = timeit.default_timer()
    size = sys.getsizeof(message)
    print("Received size: {}".format(str(size)))
    payload = json.loads(message.payload)
    del payload['prediction']
    overall_delay = message_arrived - payload['message_sent']
    payload['overall_delay'] = overall_delay
    payload['message_arrived'] = message_arrived
    payload['processing_delay'] = payload['processing_end_time'] - payload['processing_start_time']
    payload['network_delay'] = payload['overall_delay'] - payload['processing_delay']
    print(payload)
    stats.write("{},{},{},{},{},{},{}\n"
                .format(payload['message_sent'],
                        payload['processing_start_time'],
                        payload['processing_end_time'],
                        payload['message_arrived'],
                        payload['network_delay'],
                        payload['processing_delay'],
                        payload['overall_delay']))
    print "Diff between message_sent and message_arrived: {}".format(message_arrived - payload['message_sent'])


MAX_DISCOVERY_RETRIES = 10
GROUP_CA_PATH = "./groupCA/"

rootCAPath = './secrets/AmazonRootCA1.pem'
certificatePath = './secrets/3dde428b13-certificate.pem.crt'
privateKeyPath = './secrets/3dde428b13-private.pem.key'
thingName = 'MeasurementSensor'
clientId = thingName
thingName = thingName
response_topic = 'object_classification/response'
request_topic = 'object_classification/request'

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

myMQTTClient = AWSIoTMQTTClient('AWSLambdaDevice')
myMQTTClient.configureEndpoint('a2ks8xis7xopez-ats.iot.eu-central-1.amazonaws.com', 8883)
myMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

myMQTTClient.connect()
myMQTTClient.subscribe(response_topic, 0, customOnMessage)

i = 0

try:
    while True and i < 3:
        i += 1
        fd = open('test.jpg')
        img_str = fd.read()
        b64 = base64.b64encode(img_str)
        message = {'message': b64, 'message_sent': timeit.default_timer()}
        messageJson = json.dumps(message)
        size = sys.getsizeof(messageJson)
        print("Sent size: {}".format(str(size)))
        myMQTTClient.publish(request_topic, messageJson, 0)
        print('Request {} Published to topic {}\n'.format(i, request_topic))
        time.sleep(2)
except KeyboardInterrupt:
    stats.close()
    exit(0)

while True:
    try:
        print('Waiting for response')
        time.sleep(10)
    except KeyboardInterrupt:
        stats.close()
        exit(0)
