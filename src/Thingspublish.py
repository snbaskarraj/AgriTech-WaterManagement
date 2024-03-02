import boto3
import json
import os
import random
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# Initialize the IoT client for us-east-1 region
iot_client = boto3.client('iot', region_name='us-east-1')

# Directory where certificates are stored
certs_dir = "/Users/snbaskarraj/Documents/IITCapstone/AgriTech-WaterManagement/src/certificates"

# Load device configuration
config_file_path = '/Users/snbaskarraj/Documents/IITCapstone/AgriTech-WaterManagement/resources/device_config.json'
with open(config_file_path, 'r') as file:
    config = json.load(file)


# Function to publish message to AWS IoT topic
def publish_message(client_id, topic, data_type, cert_files):
    mqtt_client = AWSIoTMQTTClient(client_id)
    mqtt_client.configureEndpoint("a3afaswqeqldkp-ats.iot.us-east-1.amazonaws.com", 8883)
    mqtt_client.configureCredentials(cert_files['rootCA'], cert_files['privateKey'], cert_files['certificate'])

    # Generate random data based on type
    if data_type == "Temperature":
        value = round(random.uniform(20.0, 30.0), 2)  # Simulate temperature in Celsius
    elif data_type == "Moisture":
        value = round(random.uniform(30.0, 70.0), 2)  # Simulate soil moisture in percentage

    # Construct message
    message = {
        "sensor_id": client_id,
        "data_type": data_type,
        "value": value
    }

    # Connect and publish
    mqtt_client.connect()
    print(f"Publishing {data_type} data to topic {topic}: {message}")
    mqtt_client.publish(topic, json.dumps(message), 1)
    mqtt_client.disconnect()


# Main function to process sprinklers and their associated soil sensors
def process_sprinklers_and_sensors():
    for sprinkler in config['sprinklers']:
        sprinkler_id = sprinkler['id']
        devices_per_sprinkler = sprinkler['devices_per_sprinkler']

        # Process each soil sensor for the current sprinkler
        for i in range(1, devices_per_sprinkler + 1):
            soil_sensor_id = f"{sprinkler_id}_SoilSensor_{i}"
            client_id = soil_sensor_id  # Use soil sensor ID as MQTT client ID

            # Construct paths to the certificates
            cert_files = {
                'certificate': os.path.join(certs_dir, f"{soil_sensor_id}-certificate.pem.crt"),
                'privateKey': os.path.join(certs_dir, f"{soil_sensor_id}-private.pem.key"),
                'rootCA': os.path.join(certs_dir, "AmazonRootCA1.pem")
            }

            # Topics for publishing messages
            topic = "iot/agritech_raw"

            # Publish temperature and moisture data
            publish_message(client_id, topic, "Temperature", cert_files)
            publish_message(client_id, topic, "Moisture", cert_files)


process_sprinklers_and_sensors()
