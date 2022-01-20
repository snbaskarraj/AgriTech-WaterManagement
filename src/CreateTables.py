import boto3


def create_sprinkler_info_table(dynamodb=None):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    # Table definition
    table = dynamodb.create_table(
        TableName='sprinkler_info',
        KeySchema=[
            {
                'AttributeName': 'sprinkler_id',
                'KeyType': 'HASH'  # Partition key
            },
            {
                'AttributeName': 'timestamp',
                'KeyType': 'RANGE'  # Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'sprinkler_id',
                # AttributeType defines the data type. 'S' is string type and 'N' is number type
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'timestamp',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            # ReadCapacityUnits set to 10 strongly consistent reads per second
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10  # WriteCapacityUnits set to 10 writes per second
        }
    )
    return table


def create_sensor_info_table(dynamodb=None):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    # Table definition
    table = dynamodb.create_table(
        TableName='sensor_info',
        KeySchema=[
            {
                'AttributeName': 'sprinkler_id',
                'KeyType': 'HASH'  # Partition key
            },
            {
                'AttributeName': 'timestamp',
                'KeyType': 'RANGE'  # Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'sprinkler_id',
                # AttributeType defines the data type. 'S' is string type and 'N' is number type
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'timestamp',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            # ReadCapacityUnits set to 10 strongly consistent reads per second
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10  # WriteCapacityUnits set to 10 writes per second
        }
    )
    return table


def create_weather_info_table(dynamodb=None):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    # Table definition
    table = dynamodb.create_table(
        TableName='weather_info',
        KeySchema=[
            {
                'AttributeName': 'timestamp',
                'KeyType': 'HASH'  # Partition key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'timestamp',
                # AttributeType defines the data type. 'S' is string type and 'N' is number type
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            # ReadCapacityUnits set to 10 strongly consistent reads per second
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10  # WriteCapacityUnits set to 10 writes per second
        }
    )
    return table


def create_soil_moisture_info_table(dynamodb=None):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    # Table definition
    table = dynamodb.create_table(
        TableName='soil_sensor_info',
        KeySchema=[
            {
                'AttributeName': 'device_id',
                'KeyType': 'HASH'  # Partition key
            },
            {
                'AttributeName': 'timestamp',
                'KeyType': 'RANGE'  # Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'device_id',
                # AttributeType defines the data type. 'S' is string type and 'N' is number type
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'timestamp',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            # ReadCapacityUnits set to 10 strongly consistent reads per second
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10  # WriteCapacityUnits set to 10 writes per second
        }
    )
    return table


def create_sprinkler_actions_table(dynamodb=None):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    # Table definition
    table = dynamodb.create_table(
        TableName='sprinkler_actions',
        KeySchema=[
            {
                'AttributeName': 'sprinkler_id',
                'KeyType': 'HASH'  # Partition key
            },
            {
                'AttributeName': 'timestamp',
                'KeyType': 'RANGE'  # Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'sprinkler_id',
                # AttributeType defines the data type. 'S' is string type and 'N' is number type
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'timestamp',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            # ReadCapacityUnits set to 10 strongly consistent reads per second
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10  # WriteCapacityUnits set to 10 writes per second
        }
    )
    return table


if __name__ == '__main__':
    # sprinkler_info_table = create_sprinkler_info_table()
    # print("Status: ", sprinkler_info_table.table_status)

    sensor_info_table = create_sensor_info_table()
    print("Status: ", sensor_info_table.table_status)
    #
    # weather_info_table = create_weather_info_table()
    # print("Status: ", weather_info_table.table_status)
    #
    # soil_moisture_info_table = create_soil_moisture_info_table()
    # print("Status: ", soil_moisture_info_table.table_status)
    #
    # sprinkler_actions_table = create_sprinkler_actions_table()
    # print("Status: ", sprinkler_actions_table.table_status)
