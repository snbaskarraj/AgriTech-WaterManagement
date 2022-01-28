import argparse
import datetime
import json
import time
from pprint import pprint
from Database import get_sprinklers, get_last_action, get_sensor_data, get_weather_for_given_lat_long, \
    get_last_average_data_for_sensor
from sprinkler_action_publish import AWS


def get_all_sprinklers():
    sprinklers = get_sprinklers()
    # pprint(sprinklers['Items'])
    return sprinklers['Items']


def get_all_associated_sensors(sprinkler):
    print(f'getting associated sensors for sprinkler: {sprinkler["sprinkler_id"]}')
    sensors = get_sensor_data(sprinkler['sprinkler_id'])
    # pprint(sensors['Items'])
    return sensors['Items']


def get_list_of_sensor_device_id(sensors, device_type):
    sensor_ids = []
    for sensor in sensors:
        if sensor['device_type'] == device_type:
            sensor_ids.append(sensor['sensor_id'])
    return sensor_ids


def get_last_average_data(sensor_id):
    sensor_data = get_last_average_data_for_sensor(sensor_id)
    # pprint(sensor_data['Items'])
    return sensor_data['Items']


def get_weather_info(lat, long):
    print(f'lat: {lat}; long: {long}')
    weather_info = get_weather_for_given_lat_long(lat, long)
    # pprint(weather_info['Items'])
    return weather_info['Items']


def get_last_action_for_sprinkler(sprinkler):
    action = get_last_action(sprinkler['sprinkler_id'])
    # pprint(action['Items'])
    if action['Count'] == 0:
        return 'OFF'
    else:
        return action['Items'][0]['new_action']


def send_message(sprinkler, current_action, new_action):
    sprinkler_publisher.publish(topic, sprinkler['sprinkler_id'], current_action, new_action)
    return


def main_algorithm(config):
    print(f'Initiated main_algorithm() at: {str(datetime.datetime.now())}')

    # Fetch all sprinklers and iterate
    sprinklers = get_all_sprinklers()

    # Fetch associated devices for each sprinkler
    for sprinkler in sprinklers:
        print(f'Processing sprinkler: {sprinkler}')
        sensors = get_all_associated_sensors(sprinkler)

        # fetch device id for each sensor type to query the data
        print(f'Getting list of Temperature sensor ids')
        temp_sensor_id_list = get_list_of_sensor_device_id(sensors, 'Temperature')
        print(f'Getting list of Moisture sensor ids')
        mois_sensor_id_list = get_list_of_sensor_device_id(sensors, 'Moisture')

        # Fetch last 5 mins soil sensor data for each device
        sensor_wise_avg_temperature = {}
        sensor_wise_avg_moisture = {}

        for temp_sensor_id in temp_sensor_id_list:
            temp_sensor_data = get_last_average_data(temp_sensor_id)
            sensor_wise_avg_temperature[temp_sensor_id] = temp_sensor_data

        for mois_sensor_id in mois_sensor_id_list:
            mois_sensor_data = get_last_average_data(mois_sensor_id)
            sensor_wise_avg_moisture[mois_sensor_id] = mois_sensor_data

        pprint(f'avg_temperature_level: {sensor_wise_avg_temperature}')
        pprint(f'avg_moisture_level: {sensor_wise_avg_moisture}')

        # Fetch weather data for the lat/long
        weather_data = get_weather_info(sprinkler['lat'], sprinkler['long'])
        actual_air_temperature = weather_data[0]['temperature']
        actual_humidity = weather_data[0]['humidity']

        print(f'actual_air_temperature: {actual_air_temperature}')
        print(f'actual_humidity: {actual_humidity}')

        # check if humidity level has reached (as per configuration) then return true
        print(f'threshold_humidity: {config["threshold_humidity"]}')
        humidity_decision = actual_humidity > config['threshold_humidity']

        # check if air temperature level has reached (as per configuration) then return true
        print(f'threshold_air_temp: {config["threshold_air_temp"]}')
        air_temp_decision = actual_air_temperature > config['threshold_air_temp']

        # check for each sensor, if average soil moisture level (last 5 mins) has reached the configured value and
        # check if enough number of devices reporting to alarm, then return true else false
        switch_on_count = 0
        for avg_moisture in sensor_wise_avg_moisture:
            pprint(sensor_wise_avg_moisture[avg_moisture])
            if sensor_wise_avg_moisture[avg_moisture][0]['value'] > config['threshold_soil_mois']:
                switch_on_count = switch_on_count + 1
        mois_sensors_decision = sprinkler["min_devices_to_alarm"] < switch_on_count

        # check for each sensor, if average soil temperature level (last 5 mins) has reached the configured value and
        # check if enough number of devices reporting to alarm, then return true else false
        switch_on_count = 0
        for avg_temperature in sensor_wise_avg_temperature:
            if sensor_wise_avg_temperature[avg_temperature][0]['value'] > config['threshold_soil_temp']:
                switch_on_count = switch_on_count + 1
        temp_sensors_decision = sprinkler["min_devices_to_alarm"] < switch_on_count

        # Fetch the last action performed on this sprinkler from sprinkler_actions. If no data, then we can consider
        # the sprinkler is off, since its just setup and not switched on yet.
        sprinkler_last_action = get_last_action_for_sprinkler(sprinkler)
        print(f'Sprinkler "{sprinkler["sprinkler_id"]}" is currently switched "{sprinkler_last_action}" ')

        sprinkler_new_action = 'OFF'
        if humidity_decision & air_temp_decision & mois_sensors_decision & temp_sensors_decision & \
                (sprinkler_last_action == 'ON'):
            # if all returns true and last sprinkler action is ON, then ignore, as it might have switched ON already as
            # part of the previous schedule
            print(f'Sprinkler {sprinkler["sprinkler_id"]} should be switched on')
            sprinkler_new_action = 'ON'
        elif humidity_decision & air_temp_decision & mois_sensors_decision & temp_sensors_decision & \
                (sprinkler_last_action == 'OFF' or sprinkler_last_action is None):
            # if all returns true and last sprinkler action is OFF, then send message to switch it ON.
            print(f'Sprinkler {sprinkler["sprinkler_id"]} should be switched on')
            sprinkler_new_action = 'ON'
        elif not (humidity_decision & air_temp_decision & mois_sensors_decision & temp_sensors_decision) & \
                (sprinkler_last_action == 'OFF' or sprinkler_last_action is None):
            # if all returns false and last sprinkler action is OFF, then ignore, as it might have switched OFF
            # already as part of the previous schedule
            print(f'Sprinkler {sprinkler["sprinkler_id"]} should be switched off')
            sprinkler_new_action = 'OFF'
        elif not (humidity_decision & air_temp_decision & mois_sensors_decision & temp_sensors_decision) & \
                (sprinkler_last_action == 'ON'):
            # if all returns false and last sprinkler action is ON, then send message to switch it OFF.
            print(f'Sprinkler {sprinkler["sprinkler_id"]} should be switched off')
            sprinkler_new_action = 'OFF'

        # send appropriate action to sprinkler
        send_message(sprinkler, sprinkler_last_action, sprinkler_new_action)


def load_config(file_name):
    print('Loading configuration')
    f = open(file_name)
    json_config = json.loads(f.read())
    f.close()
    return json_config


# Read in command-line parameters
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="Your AWS IoT custom endpoint")
parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="Certificate file path")
parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="Private key file path")
parser.add_argument("-p", "--port", action="store", dest="port", type=int, default=8883, help="Port number")
parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="SprinklerAction", help="Client id")
parser.add_argument("-t", "--topic", action="store", dest="topic", default="iot/sprinkler", help="Targeted topic")

args = parser.parse_args()
endpoint = args.host
root_ca_path = args.rootCAPath
certificatePath = args.certificatePath
privateKeyPath = args.privateKeyPath
port = args.port
clientId = args.clientId
topic = args.topic

while True:
    # Load configuration
    loaded_config = load_config("../resources/sprinkler_params.json")
    sprinkler_publisher = AWS(clientId, endpoint, port, root_ca_path, certificatePath, privateKeyPath)
    main_algorithm(loaded_config)
    time.sleep(300)
