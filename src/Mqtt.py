import time
import json
import os
import logging
import paho.mqtt.client as mqtt
import AWSIoTPythonSDK.MQTTLib as AWSIoTPyMQTT
import random
import datetime

# Configure logging for AWS SDK and your application
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)  # Set to DEBUG for detailed logs
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Define ENDPOINT, TOPIC, RELATIVE DIRECTORY for CERTIFICATE AND KEYS
ENDPOINT = "a2d6fepf6zfxp2-ats.iot.us-east-1.amazonaws.com"
PATH_TO_CERT = "/Users/snbaskarraj/Documents/IITCapstone/AgriTech-WaterManagement/src/certificates"
TOPIC = "iot/agritech"

def test_mqtt_connection(endpoint, port, cert_path, key_path, root_ca_path):
    """
    A simple test to check MQTT connectivity using paho MQTT client.
    """
    client = mqtt.Client()

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("MQTT Test Connection Success")
        else:
            print(f"MQTT Test Connection Failed with code {rc}")

    client.on_connect = on_connect
    client.tls_set(ca_certs=root_ca_path, certfile=cert_path, keyfile=key_path)

    try:
        client.connect(endpoint, port, 60)
        client.loop_start()
        time.sleep(1)  # Wait a bit for the connection result
        client.loop_stop()
    except Exception as e:
        print(f"MQTT Test Connection Exception: {e}")

class AWS():
    def __init__(self, client):
        self.client_id = client
        self.device_id = client
        self.cert_path = os.path.join(PATH_TO_CERT, f"{client}-certificate.pem.crt")
        self.pvt_key_path = os.path.join(PATH_TO_CERT, f"{client}-private.pem.key")
        self.root_path = os.path.join(PATH_TO_CERT, "AmazonRootCA1.pem")
        self.myAWSIoTMQTTClient = AWSIoTPyMQTT.AWSIoTMQTTClient(self.client_id)
        self.myAWSIoTMQTTClient.configureEndpoint(ENDPOINT, 8883)
        self.myAWSIoTMQTTClient.configureCredentials(self.root_path, self.pvt_key_path, self.cert_path)
        self._connect()

    def _connect(self):
        try:
            self.myAWSIoTMQTTClient.connect()
            print(f"Connected: {self.client_id}")
        except Exception as e:
            print(f"Failed to connect {self.client_id}: {e}")

    def publish(self):
        print('Begin Publish')
        for i in range(10):
            message = {}
            value = float(random.normalvariate(99, 1.5))
            value = round(value, 1)
            timestamp = str(datetime.datetime.now())
            message['deviceid'] = self.device_id
            message['timestamp'] = timestamp
            message['datatype'] = 'Temperature'
            message['value'] = value
            messageJson = json.dumps(message)
            try:
                self.myAWSIoTMQTTClient.publish(TOPIC, messageJson, 1)
                print(f"Published: '{json.dumps(message)}' to the topic: {TOPIC}")
            except Exception as e:
                print(f"Failed to publish {self.client_id}: {e}")
            time.sleep(0.1)
        print('Publish End')

    def disconnect(self):
        try:
            self.myAWSIoTMQTTClient.disconnect()
            print(f"Disconnected: {self.client_id}")
        except Exception as e:
            print(f"Failed to disconnect {self.client_id}: {e}")

if __name__ == '__main__':
    sensor_names = [
        "SP1_SoilSensor_1", "SP1_SoilSensor_2", "SP1_SoilSensor_3",
        # Add more sensor names as needed...
    ]

    # Optionally test MQTT connection using the first sensor's certificates
    if sensor_names:
        cert_path = os.path.join(PATH_TO_CERT, f"{sensor_names[0]}-certificate.pem.crt")
        key_path = os.path.join(PATH_TO_CERT, f"{sensor_names[0]}-private.pem.key")
        root_ca_path = os.path.join(PATH_TO_CERT, "AmazonRootCA1.pem")
        test_mqtt_connection(ENDPOINT, 8883, cert_path, key_path, root_ca_path)

    sensors = []
    for sensor_name in sensor_names:
        try:
            sensor = AWS(sensor_name)
            sensors.append(sensor)
        except Exception as e:
            print(f"Failed to initialize {sensor_name}: {e}")

    # Publish data for each sensor
    for sensor in sensors:
        sensor.publish()
        sensor.disconnect()  # Ensure to disconnect after publishing
