#!/usr/bin/env python

# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.
import base64
import sys
import time
import json

from iothub_client import IoTHubClient, IoTHubTransportProvider, IoTHubMessage, IoTHubClientError

# 1) Obtain the connection string for your downstream device and to it
#    append this string GatewayHostName=<edge device hostname>;
# 2) The edge device hostname is the hostname set in the config.yaml of the Edge device
#    to which this sample will connect to.
#
# The resulting string should look like the following
# "HostName=<iothub_host_name>;DeviceId=<device_id>;SharedAccessKey=<device_key>;GatewayHostName=<edge device hostname>"
CONNECTION_STRING = "HostName=serverless-edge-test-hub.azure-devices.net;DeviceId=CameraSensor;SharedAccessKey=YHL7GoLgtoBf9UHSpoJu2cOCKpqZJv2xT9nWzigYEhA=;GatewayHostName=raspberrypi"

# Path to the Edge trusted root CA certificate
TRUSTED_ROOT_CA_CERTIFICATE_PATH = "azure-iot-test-only.root.ca.cert.pem"

# Supported IoTHubTransportProvider protocols are: MQTT, MQTT_WS, AMQP, AMQP_WS and HTTP
PROTOCOL = IoTHubTransportProvider.MQTT

stats = open('stats_device.json', 'a+')

# Provide the Azure IoT device client the trusted certificate contents
# via set_option with the X509
# Edge root CA certificate that was used to setup the Edge runtime
def set_certificates(client):
    if len(TRUSTED_ROOT_CA_CERTIFICATE_PATH) > 0:
        cert_data = ''
        with open(TRUSTED_ROOT_CA_CERTIFICATE_PATH, 'rb') as cert_file:
            cert_data = cert_file.read()
        try:
            client.set_option("TrustedCerts", cert_data)
            print ("set_option TrustedCerts successful")
        except IoTHubClientError as iothub_client_error:
            print ("set_option TrustedCerts failed (%s)" % iothub_client_error)
            sys.exit(1)


def image_classification_response(eper):
    print(eper)



def send_confirmation_callback(message, result, user_context):
    print(sys.getsizeof(result))
    response_arrived = time.time()
    original_message = message.get_string()
    size = sys.getsizeof(original_message)
    print("Received size: {}".format(str(size)))
    payload = json.loads(original_message)
    del payload['message']
    diff = response_arrived - payload['message_sent']
    payload['diff'] = diff
    payload['message_arrived'] = response_arrived
    print(payload)
    # stats.write("{},\n".format(json.dumps(payload)))
    print("Diff between message_sent and message_arrived: %d" % (response_arrived - payload['message_sent']))



if __name__ == '__main__':
    client = IoTHubClient(CONNECTION_STRING, PROTOCOL)
    set_certificates(client)

    i = 0

    try:
        while True and i < 500:
            with open('test.jpg', 'rb') as fd:
                i += 1
                # fd = open('test.jpg')
                img_str = fd.read()
                b64 = base64.b64encode(img_str)
                b64string = b64.decode('utf-8')
                message = {'message': b64string, 'message_sent': time.time()}
                messageJson = json.dumps(message)
                size = sys.getsizeof(message)
                iot_hub_message = IoTHubMessage(messageJson)
                print("Sent size: {}".format(str(size)))
                client.send_event_async(iot_hub_message, send_confirmation_callback, None)
                print('Request {}\n'.format(i))
                time.sleep(1)
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
