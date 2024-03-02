import os
import json
import logging
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# AWS IoT Core and Certificates Directory
endpoint = "a3afaswqeqldkp-ats.iot.us-east-1.amazonaws.com"
port = 8883
certs_dir = "/Users/snbaskarraj/Documents/IITCapstone/AgriTech-WaterManagement/src/certificates"

# Things and their sensors
things = [
    "SP1", "SP1_SoilSensor_1", "SP1_SoilSensor_2", "SP1_SoilSensor_3", "SP1_SoilSensor_4", "SP1_SoilSensor_5",
    "SP2", "SP2_SoilSensor_1", "SP2_SoilSensor_2", "SP2_SoilSensor_3", "SP2_SoilSensor_4", "SP2_SoilSensor_5",
    "SP3", "SP3_SoilSensor_1", "SP3_SoilSensor_2", "SP3_SoilSensor_3", "SP3_SoilSensor_4", "SP3_SoilSensor_5",
    "SP4", "SP4_SoilSensor_1", "SP4_SoilSensor_2", "SP4_SoilSensor_3", "SP4_SoilSensor_4", "SP4_SoilSensor_5",
    "SP5", "SP5_SoilSensor_1", "SP5_SoilSensor_2", "SP5_SoilSensor_3", "SP5_SoilSensor_4", "SP5_SoilSensor_5",
    "SP6", "SP6_SoilSensor_1"
]

# Function to create and configure MQTT client
def create_mqtt_client(client_id, cert_file, key_file):
    client = AWSIoTMQTTClient(client_id)
    client.configureEndpoint(endpoint, port)
    client.configureCredentials(os.path.join(certs_dir, "AmazonRootCA1.pem"),
                                os.path.join(certs_dir, key_file),
                                os.path.join(certs_dir, cert_file))
    client.configureAutoReconnectBackoffTime(1, 32, 20)
    client.configureOfflinePublishQueueing(-1)  # Infinite offline publish queueing
    client.configureConnectDisconnectTimeout(10)  # 10 sec
    client.configureMQTTOperationTimeout(5)  # 5 sec
    return client

# Function to publish messages for each thing
def publish_messages_for_things(things):
    for thing in things:
        # Skip if it's a base sprinkler without sensors
        if not thing.endswith("_SoilSensor_1") and not thing.endswith("_SoilSensor_2") and not thing.endswith("_SoilSensor_3") and not thing.endswith("_SoilSensor_4") and not thing.endswith("_SoilSensor_5"):
            continue

        client_id = thing
        cert_file = f"{thing}-certificate.pem.crt"
        key_file = f"{thing}-private.pem.key"

        # Create MQTT client and connect
        mqtt_client = create_mqtt_client(client_id, cert_file, key_file)
        mqtt_client.connect()
        logging.info(f"Connected to AWS IoT with client ID: {client_id}")

        try:
            # Publish message to the topic
            topic = "iot/agritech_raw"
            message = {"temperature": 22.5, "humidity": 48.2}  # Example message
            publish_message(mqtt_client, topic, message)
        finally:
            mqtt_client.disconnect()
            logging.info(f"Disconnected from AWS IoT for {client_id}")

# Main execution
if __name__ == "__main__":
    publish_messages_for_things(things)
