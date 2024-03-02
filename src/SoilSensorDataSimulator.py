'''
/*
 * Copyright 2010-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.

 * This  File is modified by GreatLearning.in for the educational purposes.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */
 '''

import argparse
import datetime
import json
import logging
import random
import time

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from AWSIoTPythonSDK.core.protocol.internal.defaults import DEFAULT_OPERATION_TIMEOUT_SEC
from AWSIoTPythonSDK.exception.AWSIoTExceptions import publishTimeoutException

from Database import get_all_sensor_data


def publish_soil_moisture_data():
    message = {}

    sensors = get_all_sensor_data()
    for sensor in sensors:
        if device_type == sensor['device_type']:
            try:
                if device_type == 'Temperature':
                    value = float(random.normalvariate(99, 1.5))
                    value = round(value, 1)
                else:
                    value = int(random.normalvariate(90, 3.0))

                message['device_id'] = sensor['sensor_id']
                message['timestamp'] = str(datetime.datetime.now())
                message['datatype'] = device_type
                message['value'] = value

                message_json = json.dumps(message)
                myAWSIoTMQTTClient.publish(topic, message_json, 1)
                print('Published topic %s: %s\n' % (topic, message_json))
            except publishTimeoutException:
                print(
                    "Unstable connection detected. Wait for {} seconds. No data is pushed on IoT core from {} to {}.".format(
                        DEFAULT_OPERATION_TIMEOUT_SEC,
                        (datetime.datetime.now() - datetime.timedelta(seconds=DEFAULT_OPERATION_TIMEOUT_SEC)),
                        datetime.datetime.now()))



# Read in command-line parameters
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="Your AWS IoT custom endpoint")
parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="Certificate file path")
parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="Private key file path")
parser.add_argument("-p", "--port", action="store", dest="port", default=8883, type=int, help="Port number override")
parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="SensorSimulator", help="Client id")
parser.add_argument("-t", "--topic", action="store", dest="topic", default="sdk/test/Python", help="Targeted topic")
parser.add_argument("-d", "--device_type", action="store", required=True, dest="device_type", default="Temperature",
                    help="Device Type: Temperature or Moisture")

args = parser.parse_args()
host = args.host
rootCAPath = args.rootCAPath
certificatePath = args.certificatePath
privateKeyPath = args.privateKeyPath
port = args.port
clientId = args.clientId
topic = args.topic
device_type = args.device_type


# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)



# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
myAWSIoTMQTTClient.configureEndpoint(host, port)
myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(30)  # 5 sec

# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()

now = time.time()
while True:
    try:
        publish_soil_moisture_data()
        time.sleep(5)
    except KeyboardInterrupt:
        break

print("Initiate the connection closing process from AWS.")
myAWSIoTMQTTClient.disconnect()
print("Connection closed.")
