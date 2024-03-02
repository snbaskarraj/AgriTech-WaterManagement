import argparse
import datetime
import json
import logging
import random
import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from AWSIoTPythonSDK.exception.AWSIoTExceptions import publishTimeoutException, connectTimeoutException

# Setup argparse to handle command-line arguments
parser = argparse.ArgumentParser(description='Publish soil sensor data to AWS IoT.')
parser.add_argument('-e', '--endpoint', required=True, help='Your AWS IoT custom endpoint')
parser.add_argument('-r', '--rootCA', required=True, help='Root CA file path')
parser.add_argument('-c', '--cert', required=True, help='Certificate file path')
parser.add_argument('-k', '--key', required=True, help='Private key file path')
parser.add_argument('-t', '--topic', required=True, help='MQTT topic to publish the data.')
parser.add_argument('-d', '--device_type', required=True, choices=['Temperature', 'Moisture'], help='Type of device to simulate data for.')
args = parser.parse_args()

# Initialize logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure MQTT client with actual AWS IoT Core endpoint and credentials
myAWSIoTMQTTClient = AWSIoTMQTTClient("uniqueClientIdentifier")
myAWSIoTMQTTClient.configureEndpoint(args.endpoint, 8883)
myAWSIoTMQTTClient.configureCredentials(args.rootCA, args.key, args.cert)

def connect_to_aws_iot():
    try:
        myAWSIoTMQTTClient.connect()
        logging.info("Connected to AWS IoT.")
        return True
    except connectTimeoutException as e:
        logging.error(f"Failed to connect to AWS IoT: {e}")
        return False

def get_all_sensor_data():
    # Adjust this function based on args.device_type if needed
    sensors = [{"device_id": "SP5_SoilSensor_4", "device_type": args.device_type, "value": 25.0}]
    return sensors

def publish_soil_moisture_data(topic):
    if not connect_to_aws_iot():
        logging.error("Aborting publish due to connection failure.")
        return
    sensors = get_all_sensor_data()
    for sensor in sensors:
        message = {"device_id": sensor["device_id"], "value": sensor["value"], "datatype": sensor["device_type"], "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        message_json = json.dumps(message)
        attempt_publish(topic, message_json)

def attempt_publish(topic, message_json, retry_count=3):
    for attempt in range(retry_count):
        try:
            myAWSIoTMQTTClient.publish(topic, message_json, 1)
            logging.info(f'Published to {topic}: {message_json}')
            break
        except publishTimeoutException:
            logging.warning(f'Publish attempt {attempt + 1} timed out. Retrying...')
            time.sleep(1)
    else:
        logging.error(f'Failed to publish after {retry_count} attempts.')

if __name__ == "__main__":
    # Verify the network connectivity and AWS IoT Core settings
    if not connect_to_aws_iot():
        logging.error("Please verify your AWS IoT Core Endpoint, certificate paths, AWS IoT Core policies, and network connectivity.")
        exit(1)

    # Main loop to publish sensor data
    while True:
        try:
            publish_soil_moisture_data(args.topic)
            time.sleep(5)  # Adjust as necessary
        except KeyboardInterrupt:
            logging.info("Stopping data publication...")
            break

    myAWSIoTMQTTClient.disconnect()
    logging.info("Disconnected from AWS IoT.")
