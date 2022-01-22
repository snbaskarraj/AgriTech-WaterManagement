import datetime
import json
import time
from pprint import pprint

from dateutil.relativedelta import relativedelta

from src.Database import get_sprinklers, get_sensor_data_for_time_range, get_last_action, get_sensor_data, \
    get_weather_for_given_lat_long
from src.sprinkler_action_publish import AWS


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


def get_sensor_data_for_last_x_mins(sprinkler_id, sensor_id, mins):
    current_time = datetime.datetime.now()
    start_time = current_time - relativedelta(minutes=mins)
    end_time = current_time
    sensor_data = get_sensor_data_for_time_range(sprinkler_id, sensor_id, start_time, end_time)
    # pprint(sensor_data['Items'])
    return sensor_data['Items']


def find_average_of_sensor_data(sensor_data_list):
    total = count = 0
    for sensor_data in sensor_data_list:
        total = total + sensor_data['value']
        count = count + 1

    if count == 0:
        return
    return total / count


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
        return action['Items'][0]['action']


def send_message(sprinkler, action):
    sprinkler_sensor = AWS(sprinkler['sprinkler_id'], "thing_1_certificate_filename", "thing_1_private_key_filename", action)
    sprinkler_sensor.publish()
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
            temp_sensor_data = get_sensor_data_for_last_x_mins(sprinkler['sprinkler_id'], temp_sensor_id, 5)
            avg_val = find_average_of_sensor_data(temp_sensor_data)
            sensor_wise_avg_temperature[temp_sensor_id] = avg_val

        for mois_sensor_id in mois_sensor_id_list:
            mois_sensor_data = get_sensor_data_for_last_x_mins(sprinkler['sprinkler_id'], mois_sensor_id, 5)
            avg_val = find_average_of_sensor_data(mois_sensor_data)
            sensor_wise_avg_moisture[mois_sensor_id] = avg_val

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
            if sensor_wise_avg_moisture[avg_moisture] > config['threshold_soil_mois']:
                switch_on_count = switch_on_count + 1
        mois_sensors_decision = sprinkler["min_devices_to_alarm"] > switch_on_count

        # check for each sensor, if average soil temperature level (last 5 mins) has reached the configured value and
        # check if enough number of devices reporting to alarm, then return true else false
        switch_on_count = 0
        for avg_temperature in sensor_wise_avg_temperature:
            if sensor_wise_avg_temperature[avg_temperature] > config['threshold_soil_temp']:
                switch_on_count = switch_on_count + 1
        temp_sensors_decision = sprinkler["min_devices_to_alarm"] > switch_on_count

        # Fetch the last action performed on this sprinkler from sprinkler_actions. If no data, then we can consider
        # the sprinkler is off, since its just setup and not switched on yet.
        sprinkler_last_action = get_last_action_for_sprinkler(sprinkler)

        # if all returns true and last sprinkler action is ON, then ignore, as it might have switched ON already as
        # part of the previous schedule
        if humidity_decision & air_temp_decision & mois_sensors_decision & temp_sensors_decision & \
                (sprinkler_last_action == 'ON'):
            pass

        # if all returns true and last sprinkler action is OFF, then send message to switch it ON.
        if humidity_decision & air_temp_decision & mois_sensors_decision & temp_sensors_decision & \
                (sprinkler_last_action == 'OFF' or sprinkler_last_action is None):
            send_message(sprinkler, 'ON')

        # if all returns false and last sprinkler action is OFF, then ignore, as it might have switched OFF already as
        # part of the previous schedule
        if not (humidity_decision & air_temp_decision & mois_sensors_decision & temp_sensors_decision) & \
               (sprinkler_last_action == 'OFF' or sprinkler_last_action is None):
            pass

        # if all returns false and last sprinkler action is ON, then send message to switch it OFF.
        if not (humidity_decision & air_temp_decision & mois_sensors_decision & temp_sensors_decision) & \
               (sprinkler_last_action == 'ON'):
            send_message(sprinkler, 'OFF')


def load_config(file_name):
    print('Loading configuration')
    f = open(file_name)
    json_config = json.loads(f.read())
    f.close()
    return json_config


while True:
    # Load configuration
    loaded_config = load_config("../resources/sprinkler_params.json")
    main_algorithm(loaded_config)
    time.sleep(300)

