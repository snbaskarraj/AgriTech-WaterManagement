import argparse
import datetime
import json
import logging
import random
import time
import os

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
                topic = f"iot/agritech_raw -d {device_type}"
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
parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host",
                    help="Your AWS IoT custom endpoint")
parser.add_argument("-p", "--port", action="store", dest="port", default=8883, type=int,
                    help="Port number override")
parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="SensorSimulator",
                    help="Client id")
parser.add_argument("-d", "--device_type", action="store", required=True, dest="device_type",
                    default="Temperature",
                    help="Device Type: Temperature or Moisture")

args = parser.parse_args()
host = args.host
port = args.port
clientId = args.clientId
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

# Read the certificates file
certificates_file_path = "/Users/snbaskarraj/Documents/IITCapstone/AgriTech-WaterManagement/src/certificates"
with open(certificates_file_path, "r") as certificates_file:
    certificates_data = json.load(certificates_file)

# Iterate through each certificate in the data
for certificate_data in certificates_data:
    # Extract certificate data
    certificate_pem = certificate_data["certificatePem"]
    private_key = certificate_data["privateKey"]
    public_key = certificate_data["publicKey"]

    # AWSIoTMQTTClient certificate configuration
    myAWSIoTMQTTClient.configureCredentials(certificate_pem, private_key, certificate_pem)

    # AWSIoTMQTTClient connection configuration
    myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
    myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
    myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
    myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

    # Connect and subscribe to AWS IoT
    myAWSIoTMQTTClient.connect()

    # Publish data
    publish_soil_moisture_data()

    # Disconnect from AWS IoT
    myAWSIoTMQTTClient.disconnect()

print("Connection closed.")
