import boto3
import json

# Initialize the IoT client for us-east-1 region with your account ID
iot_client = boto3.client('iot', region_name='us-east-1')

# Policy document for publishing to specific MQTT topics
policy_document = {
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Action": "iot:Publish",
        "Resource": [
            "arn:aws:iot:us-east-1:645588154117:topic/iot/agritech_raw",
            "arn:aws:iot:us-east-1:645588154117:topic/iot/sprinkler"
        ]
    }]
}


# Ensure Thing Type exists or create it, and check for policy existence or create it
def ensure_resources(thing_type_name, policy_name, policy_document):
    # Check and create Thing Type
    try:
        iot_client.describe_thing_type(thingTypeName=thing_type_name)
        print(f"Thing Type {thing_type_name} already exists.")
    except iot_client.exceptions.ResourceNotFoundException:
        iot_client.create_thing_type(thingTypeName=thing_type_name)
        print(f"Thing Type {thing_type_name} created.")
    # Check and create Policy
    try:
        iot_client.get_policy(policyName=policy_name)
        print(f"Policy {policy_name} already exists.")
    except iot_client.exceptions.ResourceNotFoundException:
        iot_client.create_policy(policyName=policy_name, policyDocument=json.dumps(policy_document))
        print(f"Policy {policy_name} created.")


# Create Thing and its certificate, attach the policy
def create_thing_and_certificate(thing_name, thing_type, policy_name):
    thing_response = iot_client.create_thing(thingName=thing_name, thingTypeName=thing_type)
    cert_response = iot_client.create_keys_and_certificate(setAsActive=True)
    iot_client.attach_thing_principal(thingName=thing_name, principal=cert_response['certificateArn'])
    iot_client.attach_policy(policyName=policy_name, target=cert_response['certificateArn'])

    print(f"Thing {thing_name} with type {thing_type} created.")
    print(f"Certificate {cert_response['certificateId']} attached with details:")
    print(json.dumps({
        'certificatePem': cert_response['certificatePem'],
        'privateKey': cert_response['keyPair']['PrivateKey'],
        'publicKey': cert_response['keyPair']['PublicKey']
    }, indent=4))


# Load device configuration from a file
config_file_path = '/Users/snbaskarraj/Documents/IITCapstone/AgriTech-WaterManagement/resources/device_config.json'
with open(config_file_path, 'r') as file:
    config = json.load(file)

# Names for your things, types, and policy
policy_name = "SoilSensorSprinklerPublishPolicy"
thing_type_name_sprinkler = "Sprinkler"
thing_type_name_soil_sensor = "SoilSensor"

# Ensure resources
ensure_resources(thing_type_name_sprinkler, policy_name, policy_document)
ensure_resources(thing_type_name_soil_sensor, policy_name, policy_document)

# Create Things for Sprinklers and Soil Sensors
for sprinkler in config['sprinklers']:
    create_thing_and_certificate(sprinkler['id'], thing_type_name_sprinkler, policy_name)
    for i in range(sprinkler['devices_per_sprinkler']):
        soil_sensor_name = f"{sprinkler['id']}_SoilSensor_{i + 1}"
        create_thing_and_certificate(soil_sensor_name, thing_type_name_soil_sensor, policy_name)
