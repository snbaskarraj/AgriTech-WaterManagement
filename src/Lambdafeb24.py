import boto3
from decimal import Decimal
import json
from datetime import datetime

# Initialize AWS SDK clients
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
iot_data = boto3.client('iot-data', region_name='us-east-1')

# DynamoDB table name
table_name = 'soil_sensor_decision'


# Function to process incoming messages
def lambda_handler(event, context):
    # Example event parsing (adjust based on actual payload structure)
    device_id = event.get('device_id')
    datatype = event.get('datatype')
    value = event.get('value')
    timestamp = event.get('timestamp')

    # Decision logic placeholder (implement your own logic here)
    should_sprinkler_run = make_decision(datatype, value)

    # Log decision to DynamoDB
    log_decision_to_dynamodb(device_id, datatype, value, timestamp, should_sprinkler_run)

    # Command sprinkler based on decision
    command_sprinkler(device_id, should_sprinkler_run)


def make_decision(datatype, value):
    # Placeholder for decision-making logic
    # Return True to turn the sprinkler on, False to keep it off
    return True if value < some_threshold else False


def log_decision_to_dynamodb(device_id, datatype, value, timestamp, decision):
    table = dynamodb.Table(table_name)
    try:
        table.put_item(Item={
            'device_id': device_id,
            'timestamp': timestamp,
            'datatype': datatype,
            'value': Decimal(str(value)),  # Convert to Decimal for DynamoDB
            'decision': 'ON' if decision else 'OFF'
        })
    except Exception as e:
        print(f"Error logging decision to DynamoDB: {str(e)}")


def command_sprinkler(device_id, command):
    # Determine the appropriate sprinkler based on the device_id
    # This example assumes a simplistic mapping
    sprinkler_topic = f'sprinklers/{device_id}/command'
    message = {
        'command': 'ON' if command else 'OFF',
        'timestamp': datetime.utcnow().isoformat()
    }
    try:
        iot_data.publish(
            topic=sprinkler_topic,
            qos=1,
            payload=json.dumps(message)
        )
    except Exception as e:
        print(f"Error publishing sprinkler command: {str(e)}")


# Example threshold for decision making
some_threshold = 30
