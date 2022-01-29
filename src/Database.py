import datetime
from pprint import pprint

from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
import boto3


def get_sprinklers():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    sprinkler_info_table = dynamodb.Table('sprinkler_info')

    try:
        response = sprinkler_info_table.scan()
        # pprint(response)
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return response


def get_sprinkler_data(sprinkler_id):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    sprinkler_info_table = dynamodb.Table('sprinkler_info')

    try:
        response = sprinkler_info_table.query(KeyConditionExpression=Key('sprinkler_id').eq(sprinkler_id) &
                                                                     Key('timestamp').lt(str(datetime.datetime.now())))
        # pprint(response)
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return response


def get_all_sensor_data():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    sensor_info_table = dynamodb.Table('sensor_info')

    try:
        # kwargs = {'KeyConditionExpression': Key('sprinkler_id').eq(sprinkler_id)}
        # response = sensor_info_table.query(**kwargs)
        response = sensor_info_table.scan()
        # pprint(response)
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return response['Items']


def get_sensor_data(sprinkler_id):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    sensor_info_table = dynamodb.Table('sensor_info')

    try:
        # kwargs = {'KeyConditionExpression': Key('sprinkler_id').eq(sprinkler_id)}
        # response = sensor_info_table.query(**kwargs)
        response = sensor_info_table.query(KeyConditionExpression=Key('sprinkler_id').eq(sprinkler_id))
        # pprint(response)
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return response


def get_sensor_data_for_time_range(sensor_id, start_time, end_time):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    sensor_info_table = dynamodb.Table('soil_sensor_info')

    try:
        # response = sensor_info_table.query(
        #     KeyConditionExpression=Key('device_id').eq(sensor_id) &
        #                            Key('timestamp').between(str(start_time), str(end_time))
        #                                    )
        kwargs = {'KeyConditionExpression': Key('device_id').eq(sensor_id) &
                                            Key('timestamp').between(str(start_time), str(end_time)),
                  'ScanIndexForward': False,
                  'Limit': 2}
        response = sensor_info_table.query(**kwargs)
        # pprint(response)
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return response


def get_last_average_data_for_sensor(sensor_id):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    sensor_info_table = dynamodb.Table('soil_sensor_info')

    try:
        kwargs = {'KeyConditionExpression': Key('device_id').eq(sensor_id),
                  'ScanIndexForward': False,
                  'Limit': 1}
        response = sensor_info_table.query(**kwargs)
        # pprint(response)
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return response


def get_last_action(sprinkler_id):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    sprinkler_action_table = dynamodb.Table('sprinkler_actions')

    try:
        # response = sprinkler_action_table.query(KeyConditionExpression=Key('sprinkler_id').eq(sprinkler_id))
        kwargs = {'KeyConditionExpression': Key('sprinkler_id').eq(sprinkler_id),
                  'ScanIndexForward': False,
                  'Limit': 1}
        response = sprinkler_action_table.query(**kwargs)
        # pprint(response)
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return response


def get_weather_for_given_lat_long(lat, long):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    sensor_info_table = dynamodb.Table('weather_info')

    try:
        lat_long = str(lat) + "_" + str(long)
        # response = sensor_info_table.query(KeyConditionExpression=Key('lat_long').eq(lat_long))
        kwargs = {'KeyConditionExpression': Key('lat_long').eq(lat_long),
                  'ScanIndexForward': False,
                  'Limit': 1}
        response = sensor_info_table.query(**kwargs)
        # pprint(response)
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return response


# def put_device_info(device_id, timestamp, device_type, lat, long, sprinkler_id, min_devices_to_alarm, dynamodb=None):
#     dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
#     device_info = dynamodb.Table('device_info')
#
#     try:
#         response = device_info.put_item(
#             Item={
#                 'device_id': device_id,
#                 'timestamp': timestamp,
#                 'device_type': device_type,
#                 'lat': lat,
#                 'long': long,
#                 'sprinkler_id': sprinkler_id,
#                 'min_devices_to_alarm': min_devices_to_alarm
#             }
#         )
#
#         return response
#     except ClientError as e:
#         print(e.response['Error']['Message'])


def put_sprinkler_info(sprinkler_id, timestamp, device_type, lat, long, min_devices_to_alarm):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    device_info = dynamodb.Table('sprinkler_info')

    try:
        response = device_info.put_item(
            Item={
                'sprinkler_id': sprinkler_id,
                'timestamp': timestamp,
                'device_type': device_type,
                'lat': lat,
                'long': long,
                'min_devices_to_alarm': min_devices_to_alarm
            }
        )

        return response
    except ClientError as e:
        print(e.response['Error']['Message'])


def put_sensor_info(sensor_id, timestamp, device_type, sprinkler_id, dynamodb=None):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    sensor_info = dynamodb.Table('sensor_info')

    try:
        response = sensor_info.put_item(
            Item={
                'sensor_id': sensor_id,
                'timestamp': timestamp,
                'device_type': device_type,
                'sprinkler_id': sprinkler_id
            }
        )

        return response
    except ClientError as e:
        print(e.response['Error']['Message'])


def put_weather_info(lat, long, timestamp, temperature, humidity, dynamodb=None):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    weather_info = dynamodb.Table('weather_info')

    try:
        response = weather_info.put_item(
            Item={
                'timestamp': timestamp,
                'lat': lat,
                'long': long,
                'temperature': temperature,
                'humidity': humidity
            }
        )

        return response
    except ClientError as e:
        print(e.response['Error']['Message'])


def put_soil_sensor_data(device_id, timestamp, device_type, value, dynamodb=None):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    soil_sensor_data = dynamodb.Table('soil_sensor_data')

    try:
        response = soil_sensor_data.put_item(
            Item={
                'device_id': device_id,
                'timestamp': timestamp,
                'device_type': device_type,
                'value': value
            }
        )

        return response
    except ClientError as e:
        print(e.response['Error']['Message'])


def put_sprinkler_actions(device_id, timestamp, action, dynamodb=None):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    sprinkler_actions = dynamodb.Table('sprinkler_info')

    try:
        response = sprinkler_actions.put_item(
            Item={
                'device_id': device_id,
                'timestamp': timestamp,
                'action': action
            }
        )

        return response
    except ClientError as e:
        print(e.response['Error']['Message'])
