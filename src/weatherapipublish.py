import argparse
import json
import datetime
import requests
import boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Key
import time

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

api_key = "54c569d5fe4ca62779e9a5577ed75c04"
lat = "48.208176" #default
lon = "16.373819" #default


# to query dynamodb
def query_db():
    table = dynamodb.Table('sprinkler_info')
    resp = table.scan()
    # print(resp['Items'])
    if 'Items' in resp:
        lat = resp['Items'][0]['lat']
        lon = resp['Items'][0]['long']
        return str(lat) + "_" + str(lon)


# to store in dyanamodb
def put_item_in_database(data):
    
    table = dynamodb.Table('weather_info')
    timestamp = str(datetime.datetime.now())
    temperature = data["current"]["temp"]
    humidity = data["current"]["humidity"]

    resp = table.put_item(
            Item={
                'timestamp': timestamp,
                'lat_long': lat_long,
                'temperature': Decimal(str(temperature)),
                'humidity': Decimal(str(humidity))
            }
        )
    print(resp)
    if 'Item' in resp:
        print(resp['Item'])


lat_long = query_db() #gets the lat and long

# print(lat)
# print(lon)
print(lat_long)

# ONE_HOUR = 1 * 60 * 60  # seconds
# ONE_MINUTE = 1 * 60  # seconds
#
# start_time = time.time()
#
# current_time = start_time
# while current_time <= start_time + ONE_HOUR - ONE_MINUTE:
#     time.sleep(ONE_MINUTE)
#     current_time = time.time()
#     url = "https://api.openweathermap.org/data/2.5/onecall?lat=%s&lon=%s&appid=%s&units=metric" % (lat, lon, api_key)
#     response = requests.get(url)
#     data = json.loads(response.text)
#
#     #print(data)
#
#     put_item_in_database(data) #writes into db


# Read in command-line parameters
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--time", action="store", required=True, type=int, dest="sleep_time", default=30,
                    help="Time interval in secs to run")
args = parser.parse_args()
sleep_time = args.sleep_time

while True:
    url = "https://api.openweathermap.org/data/2.5/onecall?lat=%s&lon=%s&appid=%s&units=metric" % (lat, lon, api_key)
    response = requests.get(url)
    data = json.loads(response.text)
    # print(data)

    # writes into db
    put_item_in_database(data)

    time.sleep(sleep_time)
