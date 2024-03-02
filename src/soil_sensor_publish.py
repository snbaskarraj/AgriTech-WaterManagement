import time
import json
import AWSIoTPythonSDK.MQTTLib as AWSIoTPyMQTT
import random
import datetime
import os
import logging

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
            # Implement a retry mechanism or log the error for further investigation

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
    sensors = []  # List to store sensor objects

    # List your sensors here, simplified for demonstration
    sensor_names = [
        "SP1_SoilSensor_1", "SP1_SoilSensor_2", "SP1_SoilSensor_3", "SP1_SoilSensor_4", "SP1_SoilSensor_5",
        "SP2_SoilSensor_1", "SP2_SoilSensor_2", "SP2_SoilSensor_3", "SP2_SoilSensor_4", "SP2_SoilSensor_5",
        "SP3_SoilSensor_1", "SP3_SoilSensor_2", "SP3_SoilSensor_3", "SP3_SoilSensor_4", "SP3_SoilSensor_5",
        "SP4_SoilSensor_1", "SP4_SoilSensor_2", "SP4_SoilSensor_3", "SP4_SoilSensor_4", "SP4_SoilSensor_5",
        "SP5_SoilSensor_1", "SP5_SoilSensor_2", "SP5_SoilSensor_3", "SP5_SoilSensor_4", "SP5_SoilSensor_5"
    ]

    # Dynamically create sensor objects
    for sensor_name in sensor_names:
        try:
            sensor = AWS(sensor_name)
            sensors.append(sensor)
        except Exception as e:
            print(f"Failed to initialize {sensor_name}: {e}")

    #
