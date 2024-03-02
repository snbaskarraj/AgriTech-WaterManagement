import boto3
import json
import os
import requests

# Initialize the IoT client for us-east-1 region with your account ID
iot_client = boto3.client('iot', region_name='us-east-1')

# Directory to save certificates
certs_dir = "/Users/snbaskarraj/Documents/IITCapstone/AgriTech-WaterManagement/src/certificates"

# Policy document for publishing to specific MQTT topics
policy_document = {
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Action": "iot:*",
        "Resource": [
            "arn:aws:iot:us-east-1:940654837868:topic/iot/agritech_raw",
            "arn:aws:iot:us-east-1:940654837868:topic/iot/sprinkler"
        ]
    }]
}

def ensure_resources(thing_type_name, policy_name, policy_document):
    try:
        iot_client.describe_thing_type(thingTypeName=thing_type_name)
        print(f"Thing Type {thing_type_name} already exists.")
    except iot_client.exceptions.ResourceNotFoundException:
        iot_client.create_thing_type(thingTypeName=thing_type_name)
        print(f"Thing Type {thing_type_name} created.")

    try:
        iot_client.get_policy(policyName=policy_name)
        print(f"Policy {policy_name} already exists.")
    except iot_client.exceptions.ResourceNotFoundException:
        iot_client.create_policy(policyName=policy_name, policyDocument=json.dumps(policy_document))
        print(f"Policy {policy_name} created.")

def create_thing_and_certificate(thing_name, thing_type, policy_name):
    thing_response = iot_client.create_thing(thingName=thing_name, thingTypeName=thing_type)
    cert_response = iot_client.create_keys_and_certificate(setAsActive=True)
    iot_client.attach_thing_principal(thingName=thing_name, principal=cert_response['certificateArn'])
    iot_client.attach_policy(policyName=policy_name, target=cert_response['certificateArn'])

    # Save certificates as files
    certificate_file_path = os.path.join(certs_dir, f"{thing_name}-certificate.pem.crt")
    private_key_file_path = os.path.join(certs_dir, f"{thing_name}-private.pem.key")
    public_key_file_path = os.path.join(certs_dir, f"{thing_name}-public.pem.key")

    with open(certificate_file_path, 'w') as cert_file:
        cert_file.write(cert_response['certificatePem'])
    with open(private_key_file_path, 'w') as private_file:
        private_file.write(cert_response['keyPair']['PrivateKey'])
    with open(public_key_file_path, 'w') as public_file:
        public_file.write(cert_response['keyPair']['PublicKey'])

    print(f"Certificates saved for {thing_name}")

# Download Amazon Root CA certificate
root_ca_url = "https://www.amazontrust.com/repository/AmazonRootCA1.pem"
root_ca_path = os.path.join(certs_dir, "AmazonRootCA1.pem")
response = requests.get(root_ca_url)
with open(root_ca_path, 'w') as root_ca_file:
    root_ca_file.write(response.text)

config_file_path = '/Users/snbaskarraj/Documents/IITCapstone/AgriTech-WaterManagement/resources/device_config.json'
with open(config_file_path, 'r') as file:
    config = json.load(file)

policy_name = "SoilSensorSprinklerPublishPolicy"
ensure_resources("Sprinkler", policy_name, policy_document)
ensure_resources("SoilSensor", policy_name, policy_document)

for sprinkler in config['sprinklers']:
    create_thing_and_certificate(sprinkler['id'], "Sprinkler", policy_name)
    for i in range(sprinkler['devices_per_sprinkler']):
        soil_sensor_name = f"{sprinkler['id']}_SoilSensor_{i+1}"
        create_thing_and_certificate(soil_sensor_name, "SoilSensor", policy_name)
