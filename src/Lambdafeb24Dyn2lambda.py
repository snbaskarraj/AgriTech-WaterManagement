import boto3
from decimal import Decimal
import json
from datetime import datetime

# Initialize AWS SDK clients
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
iot_data = boto3.client('iot-data', region_name='us-east-1')

# DynamoDB table names
info_table_name = 'soil_sensor_info'  # Table to read sensor data from
decision_table_name = 'soil_sensor_decision'  # Table to write decisions to

# Thresholds for decision making
thresholds = {
    "threshold_soil_temp": 99,
    "threshold_soil_mois": 15,
    "upper_threshold_humidity": 85,
    "upper_threshold_air_temp": 0.5,
    "lower_threshold_humidity": 75,
    "lower_threshold_air_temp": 0.2,
}

# Custom encoder for handling Decimal types in JSON serialization
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)  # Convert Decimal to float
        return json.JSONEncoder.default(self, obj)

def lambda_handler(event, context):
    # Fetch device IDs from the DynamoDB table
    device_ids = get_device_ids()
    for device_id in device_ids:
        # Proceed with the rest of the function for each device_id
        aggregated_data = read_and_aggregate_data(device_id)
        print(f"Aggregated data for {device_id}: {json.dumps(aggregated_data, cls=DecimalEncoder)}")
        should_sprinkler_run = make_decision(aggregated_data)
        print(f"Sprinkler decision for {device_id}: {'ON' if should_sprinkler_run else 'OFF'}")
        timestamp = datetime.utcnow().isoformat()
        log_decision_to_dynamodb(device_id, aggregated_data, timestamp, should_sprinkler_run)
        command_sprinkler(device_id, should_sprinkler_run)

def get_device_ids():
    table = dynamodb.Table(info_table_name)
    # Assuming 'device_id' is a primary key or an index, adjust the query accordingly
    response = table.scan(ProjectionExpression="device_id")
    device_ids = {item['device_id'] for item in response['Items']}
    return list(device_ids)

# The rest of the functions (read_and_aggregate_data, make_decision, log_decision_to_dynamodb, command_sprinkler) remain unchanged

def read_and_aggregate_data(device_id):
    table = dynamodb.Table(info_table_name)
    response = table.query(
        KeyConditionExpression='device_id = :device_id',
        ExpressionAttributeValues={':device_id': device_id},
        ScanIndexForward=False,
        Limit=10
    )
    items = response['Items']
    aggregated_data = {}
    for item in items:
        datatype = item['datatype']
        value = item['value']
        aggregated_data[datatype] = value
    return aggregated_data

def make_decision(aggregated_data):
    decisions = []
    for datatype, value in aggregated_data.items():
        if datatype == "soil_temp" and value > thresholds["threshold_soil_temp"]:
            decisions.append(True)
        elif datatype == "soil_mois" and value < thresholds["threshold_soil_mois"]:
            decisions.append(True)
        elif datatype == "humidity" and (value > thresholds["upper_threshold_humidity"] or value < thresholds["lower_threshold_humidity"]):
            decisions.append(True)
        elif datatype == "air_temp" and (value > thresholds["upper_threshold_air_temp"] or value < thresholds["lower_threshold_air_temp"]):
            decisions.append(True)
    return any(decisions)

def log_decision_to_dynamodb(device_id, aggregated_data, timestamp, decision):
    table = dynamodb.Table(decision_table_name)
    try:
        serialized_data = json.dumps(aggregated_data, cls=DecimalEncoder)
        table.put_item(Item={
            'device_id': device_id,
            'timestamp': timestamp,
            'data': serialized_data,
            'decision': 'ON' if decision else 'OFF'
        })
    except Exception as e:
        print(f"Error logging decision to DynamoDB: {str(e)}")

def command_sprinkler(device_id, command):
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
