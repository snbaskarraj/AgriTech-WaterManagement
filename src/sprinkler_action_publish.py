import time
import json
import AWSIoTPythonSDK.MQTTLib as AWSIoTPyMQTT
import datetime

# Define ENDPOINT, TOPIC, RELATIVE DIRECTORY for CERTIFICATE AND KEYS
# ENDPOINT = "a1ydwct3h0biqw-ats.iot.us-east-1.amazonaws.com"
# PATH_TO_CERT = "..\\config"
# TOPIC = "iot/sprinkler"


class AWS:
    # Constructor that accepts client id that works as client id and file names for different devices
    # This method will create the MQTT client for AWS using the credentials
    def __init__(self, client, endpoint, port, root_ca_path, certificate, private_key):
        self.client_id = client
        # self.cert_path = PATH_TO_CERT + "\\" + certificate
        # self.pvt_key_path = PATH_TO_CERT + "\\" + private_key
        # self.root_path = PATH_TO_CERT + "\\" + "AmazonRootCA1.pem"
        self.cert_path = certificate
        self.pvt_key_path = private_key
        self.root_path = root_ca_path
        self.myAWSIoTMQTTClient = AWSIoTPyMQTT.AWSIoTMQTTClient(self.client_id)
        self.myAWSIoTMQTTClient.configureEndpoint(endpoint, port)
        self.myAWSIoTMQTTClient.configureCredentials(self.root_path, self.pvt_key_path, self.cert_path)
        self._connect()

    # Connect method to establish connection with AWS IoT core MQTT
    # Connect operation will make sure that connection is established between the device and AWS MQTT
    def _connect(self):
        self.myAWSIoTMQTTClient.connect()

    # This method will publish the data on MQTT 
    # Before publishing we are configuring message to be published on MQTT
    def publish(self, topic, sprinkler_id, current_action, new_action):
        print('Begin Publish sprinkler action for: {sprinkler_id}')
        message = {}
        timestamp = str(datetime.datetime.now())
        message['sprinkler_id'] = sprinkler_id
        message['timestamp'] = timestamp
        message['current_action'] = current_action
        message['new_action'] = new_action
        message_json = json.dumps(message)
        self.myAWSIoTMQTTClient.publish(topic, message_json, 1)
        print("Published: '" + json.dumps(message) + "' to the topic: " + topic)
        time.sleep(0.1)

    # Disconnect from MQTT
    def disconnect(self):
        self.myAWSIoTMQTTClient.disconnect()
