import boto3

# Initialize clients
iam_client = boto3.client('iam')
iot_client = boto3.client('iot')

# Create IAM role for soil sensor
role_name = "soilsensorrole"
assume_role_policy_document = '''{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "iot.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}'''

try:
    iam_role = iam_client.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=assume_role_policy_document,
        Description="Role for soil sensor data processing and storage",
    )
    print(f"Created IAM Role: {role_name}")

    # Attach policies to the role
    policies = [
        'arn:aws:iam::aws:policy/service-role/AWSIoTLogging',
        'arn:aws:iam::aws:policy/service-role/AWSIoTRuleActions',
        'arn:aws:iam::aws:policy/service-role/AWSIoTThingsRegistration',
    ]
    for policy in policies:
        iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy
        )
    print(f"Attached necessary policies to {role_name}")
except Exception as e:
    print(f"Error creating/attaching policies to IAM Role: {str(e)}")

# Create IoT Core rule
rule_name = "ssp_dynamodb"
sql = "SELECT * FROM 'iot/agritech_raw'"
rule_action = {
    'dynamoDBv2': {
        'roleArn': 'arn:aws:iam::940654837868:role/soilsensorrole',
        'putItem': {
            'tableName': 'soil_sensor_info'
        }
    }
}
try:
    iot_client.create_topic_rule(
        ruleName=rule_name,
        topicRulePayload={
            'sql': sql,
            'description': 'Rule to route soil sensor data to DynamoDB',
            'actions': [rule_action],
            'ruleDisabled': False,
            'awsIotSqlVersion': '2016-03-23'
        }
    )
    print(f"Created IoT Core rule: {rule_name}")
except Exception as e:
    print(f"Error creating IoT Core rule: {str(e)}")

print("Automation script completed.")
