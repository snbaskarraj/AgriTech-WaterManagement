import subprocess
import time
import boto3
import json
import decimal
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# AWS credentials and region
aws_access_key_id = "AKIA5WA3FYBWIWZA4EHJ"
aws_secret_access_key = "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"
region_name = "us-east-1"

# Initialize AWS DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name=region_name,
                          aws_access_key_id=aws_access_key_id,
                          aws_secret_access_key=aws_secret_access_key)

# Initialize InfluxDB connection parameters
url = "http://localhost:8086"
token = "nz64nJTxvs1mnKr5n9vY45Kzd0-3hp4pde10keEDe0vbg0K4C4HS9v7WhX21bPIKlcQgk2ucHf7Rid8muZLD0g=="
org = "IIT CAPSTONE AGRITECH"
bucket = "SOILSENSOR"

# Initialize InfluxDB client
client = InfluxDBClient(url=url, token=token, org=org)

def install_influxdb():
    # Install InfluxDB using Homebrew
    subprocess.run(["brew", "install", "influxdb"])

def install_telegraf():
    # Install Telegraf using Homebrew
    subprocess.run(["brew", "install", "telegraf"])

def start_services():
    # Start InfluxDB and Telegraf services
    subprocess.run(["brew", "services", "start", "influxdb"])
    subprocess.run(["brew", "services", "start", "telegraf"])

def create_database():
    # Write dummy points to the database to create it if it doesn't exist
    write_api = client.write_api(write_options=SYNCHRONOUS)
    for value in range(5):
        point = (
            Point("measurement1")
            .tag("tagname1", "tagvalue1")
            .field("field1", value)
        )
        write_api.write(bucket=bucket, org=org, record=point)
        time.sleep(1) # separate points by 1 second

def configure_telegraf():
    # Configure Telegraf to send data to InfluxDB
    telegraf_conf_path = "/opt/homebrew/Cellar/telegraf/1.29.5/.bottle/etc/telegraf.conf"
    with open(telegraf_conf_path, "a") as file:
        file.write("\n[[outputs.influxdb]]\n")
        file.write("  urls = [\"http://localhost:8086\"]\n")
        file.write("  database = \"soil_sensors\"")

def fetch_data_from_dynamodb():
    # Fetch data from DynamoDB tables
    tables = ["sensor_info", "soil_sensor_decision", "soil_sensor_info", "sprinkler_actions", "sprinkler_info", "weather_info"]
    data = {}
    for table_name in tables:
        table = dynamodb.Table(table_name)
        response = table.scan()
        data[table_name] = response['Items']
    return data


# Inside the write_data_to_influxdb function
def write_data_to_influxdb(data):
    # Write data to the database
    write_api = client.write_api(write_options=SYNCHRONOUS)
    for table_name, items in data.items():
        for item in items:
            # Convert Decimal fields to float
            for key, value in item.items():
                if isinstance(value, decimal.Decimal):
                    item[key] = float(value)

            point = Point("dynamodb_data").tag("table_name", table_name).field("data", json.dumps(item))
            write_api.write(bucket, org, point)



def create_dashboard():
    # Wait for InfluxDB to start
    time.sleep(10)
    # Create a simple dashboard in Chronograf
    subprocess.run(["chronograf", "dashboard", "create", "soil_sensors_dashboard"])

def main():
    # Install and configure InfluxDB
    install_influxdb()
    start_services()
    create_database()

    # Install and configure Telegraf
    install_telegraf()
    configure_telegraf()

    # Start Telegraf service
    start_services()

    # Fetch data from DynamoDB
    data = fetch_data_from_dynamodb()

    # Write data to InfluxDB
    write_data_to_influxdb(data)

    # Create a dashboard in Chronograf
    create_dashboard()

if __name__ == "__main__":
    main()