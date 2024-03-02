import time
import json
import AWSIoTPythonSDK.MQTTLib as AWSIoTPyMQTT
import random
import datetime
import requests
import os
import sched

#Define ENDPOINT, TOPIC, RELATOVE DIRECTORY for CERTIFICATE AND KEYS
ENDPOINT = "a3afaswqeqldkp-ats.iot.us-east-1.amazonaws.com"
#certs_dir = "/Users/snbaskarraj/Documents/IITCapstone/AgriTech-WaterManagement/src"
#certs_dir = "/Users/snbaskarraj/Documents/IITCapstone/AgriTech-WaterManagement/certs"
certs_dir = os.path.join(os.path.dirname(__file__), "../certs")
TOPIC = "iot/agritech"

# Download Amazon Root CA certificate
#root_ca_url = "https://www.amazontrust.com/repository/AmazonRootCA1.pem"
#root_ca_path = os.path.join(certs_dir, "AmazonRootCA1.pem")
#response = requests.get(root_ca_url)
#with open(root_ca_path, 'w') as root_ca_file:
    #root_ca_file.write(response.text)

# Corrected AWS class definition
class AWS():
    # Constructor that accepts client id that works as device id and file names for different devices
    # This method will obviously be called while creating the instance
    # It will create the MQTT client for AWS using the credentials
    # Connect operation will make sure that connection is established between the device and AWS MQTT
    def __init__(self, client, certificate, private_key):
        self.client_id = client
        self.device_id = client
        self.cert_path = certs_dir + "//" + certificate
        self.pvt_key_path = certs_dir + "//" + private_key
        self.root_path = certs_dir + "//" + "AmazonRootCA1.pem"
        self.myAWSIoTMQTTClient = AWSIoTPyMQTT.AWSIoTMQTTClient(self.client_id)
        self.myAWSIoTMQTTClient.configureEndpoint(ENDPOINT, 8883)
        self.myAWSIoTMQTTClient.configureCredentials(self.root_path, self.pvt_key_path, self.cert_path)
        self._connect()

    # Connect method to establish connection with AWS IoT core MQTT
    def _connect(self):
        self.myAWSIoTMQTTClient.connect()

    # This method will publish the data on MQTT
    # Before publishing we are configuring the message to be published on MQTT
    def publish(self):
        print('Begin Publish')
        for i in range(20):
            message = {}
            value = float(random.normalvariate(99, 1.5))
            value = round(value, 1)
            timestamp = str(datetime.datetime.now())
            message['deviceid'] = self.device_id
            message['timestamp'] = timestamp
            message['datatype'] = 'Temperature'
            message['value'] = value
            messageJson = json.dumps(message)
            self.myAWSIoTMQTTClient.publish(TOPIC, messageJson, 1)
            print("Published: '" + json.dumps(message) + "' to the topic: " + TOPIC)
            time.sleep(0.1)
        print('Publish End')

    # Disconnect operation for each device
    def disconnect(self):
        self.myAWSIoTMQTTClient.disconnect()

# Main method with actual objects and method calling to publish the data in MQTT
# Again, this is a minimal example that can be extended to incorporate more devices
# Also, there can be different method calls as well based on the devices and their working.
if __name__ == '__main__':
    # Soil sensor device Objects
    soil_sensor_6 = AWS("SP1_SoilSensor_6",
                        "5d62f8ee6f6cca84b112b0de14e2de9cc887c735cb9d91786c66ffcb55961d32-certificate.pem.crt",
                        "5d62f8ee6f6cca84b112b0de14e2de9cc887c735cb9d91786c66ffcb55961d32-private.pem.key")
    soil_sensor_2 = AWS("SP1_SoilSensor_2",
                       "5d62f8ee6f6cca84b112b0de14e2de9cc887c735cb9d91786c66ffcb55961d32-certificate.pem.crt",
                       "5d62f8ee6f6cca84b112b0de14e2de9cc887c735cb9d91786c66ffcb55961d32-private.pem.key")
    soil_sensor_3 = AWS("SP1_SoilSensor_3",
                        "5d62f8ee6f6cca84b112b0de14e2de9cc887c735cb9d91786c66ffcb55961d32-certificate.pem.crt",
                        "5d62f8ee6f6cca84b112b0de14e2de9cc887c735cb9d91786c66ffcb55961d32-private.pem.key")

    for sensor in (soil_sensor_6,soil_sensor_2,soil_sensor_3):
        sensor.publish()



