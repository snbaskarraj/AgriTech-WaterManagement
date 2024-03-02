import boto3
import json
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import os

# AWS IoT Core Details
region = "us-east-1"
endpoint = "a3afaswqeqldkp-ats.iot.us-east-1.amazonaws.com"
aws_access_key_id = 'AKIAZMUANO4CSG3VIVW6'
aws_secret_access_key = '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'

# Initialize boto3 client
iot_client = boto3.client('iot', region_name=region, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

# Directory to save certificates
certs_dir = "/Users/snbaskarraj/Documents/IITCapstone/AgriTech-WaterManagement/src/cert1"
if not os.path.exists(certs_dir):
    os.makedirs(certs_dir, exist_ok=True)

def create_thing_type(type_name):
    """Create a Thing Type"""
    try:
        iot_client.create_thing_type(thingTypeName=type_name)
        print(f"Thing Type '{type_name}' created.")
    except iot_client.exceptions.ResourceAlreadyExistsException:
        print(f"Thing Type '{type_name}' already exists.")

def create_thing(thing_name, type_name):
    """Create a Thing"""
    response = iot_client.create_thing(thingName=thing_name, thingTypeName=type_name)
    print(f"Thing '{thing_name}' created.")
    return response

def create_policy(policy_name, policy_document):
    """Create an IoT Policy"""
    try:
        response = iot_client.create_policy(policyName=policy_name, policyDocument=json.dumps(policy_document))
        print(f"Policy '{policy_name}' created.")
    except iot_client.exceptions.ResourceAlreadyExistsException:
        print(f"Policy '{policy_name}' already exists.")

def create_keys_and_certificate_and_save():
    """Create Keys and Certificate and save them to files"""
    response = iot_client.create_keys_and_certificate(setAsActive=True)
    cert_id = response['certificateId']
    thing_name = f"MyThing_{cert_id}"

    # Save the certificate and keys
    with open(os.path.join(certs_dir, f"{thing_name}-certificate.pem.crt"), 'w') as cert_file:
        cert_file.write(response['certificatePem'])
    with open(os.path.join(certs_dir, f"{thing_name}-private.pem.key"), 'w') as private_key_file:
        private_key_file.write(response['keyPair']['PrivateKey'])
    with open(os.path.join(certs_dir, f"{thing_name}-public.pem.key"), 'w') as public_key_file:
        public_key_file.write(response['keyPair']['PublicKey'])
    print("Keys and certificate created and saved.")
    return response['certificateArn'], thing_name

def attach_policy(policy_name, cert_arn):
    """Attach a policy to a target (certificate)"""
    iot_client.attach_policy(policyName=policy_name, target=cert_arn)
    print(f"Policy '{policy_name}' attached to certificate.")

def attach_thing_principal(thing_name, cert_arn):
    """Attach a principal (certificate) to a thing"""
    iot_client.attach_thing_principal(thingName=thing_name, principal=cert_arn)
    print(f"Certificate attached to thing '{thing_name}'.")

def publish_to_topic(topic, message, thing_name):
    """Publish a message to an MQTT topic"""
    cert_path = os.path.join(certs_dir, f"{thing_name}-certificate.pem.crt")
    key_path = os.path.join(certs_dir, f"{thing_name}-private.pem.key")
    root_ca_path = os.path.join(certs_dir, "AmazonRootCA1.pem")

    mqtt_client = AWSIoTMQTTClient(thing_name)
    mqtt_client.configureEndpoint(endpoint, 8883)
    mqtt_client.configureCredentials(root_ca_path, key_path, cert_path)

    mqtt_client.connect()
    mqtt_client.publish(topic, json.dumps(message), 1)
    print(f"Published message to topic '{topic}'")
    mqtt_client.disconnect()

# Example usage
thing_type_name = "MyThingType"
policy_name = "MyPolicy"
policy_document = {
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Action": "iot:*",
        "Resource": "*"
    }]
}
topic = "test/topic"
message = {"key": "value"}

create_thing_type(thing_type_name)
policy_response = create_policy(policy_name, policy_document)
cert_arn, thing_name = create_keys_and_certificate_and_save()
attach_policy(policy_name, cert_arn)
thing_response = create_thing(thing_name, thing_type_name)
attach_thing_principal(thing_name, cert_arn)
publish_to_topic(topic, message, thing_name)
