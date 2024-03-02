import boto3
import datetime
from dateutil import tz
from decimal import Decimal

print('Loading function')

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')


def lambda_handler(event, context):
    # Logging the received event for debugging purposes
    print("Received event:", event)

    try:
        # Reference to the DynamoDB table
        table = dynamodb.Table('soil_sensor_decision')

        # Extracting information from the incoming IoT message
        device_id = event['device_id']
        datatype = event['datatype']
        # Convert the incoming value to Decimal directly without intermediate float conversion
        value_decimal = Decimal(str(event['value']))

        # Getting current UTC timestamp
        timestamp_utc = datetime.datetime.now(tz=tz.tzutc())
        timestamp = timestamp_utc.strftime('%Y-%m-%d %H:%M:%S')

        # Preparing the message to be stored in DynamoDB
        message = {
            'timestamp': timestamp,
            'value': value_decimal,  # Storing the value as Decimal
            'device_id': device_id,
            'datatype': datatype
        }

        # Storing the processed data in DynamoDB
        table.put_item(Item=message)

    except Exception as err:
        print(err)
