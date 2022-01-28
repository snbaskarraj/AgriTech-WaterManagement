import json
import datetime

from Database import put_sprinkler_info, put_sensor_info, get_sprinkler_data


def generate_and_populate_devices(config):
    print('Generating device ids for sprinklers and sensors and pushing it to database')

    lat = config['latitude']
    long = config['longitude']

    for sprinkler in config['sprinklers']:
        print(sprinkler['id'])

        sprinkler_id = sprinkler['id']
        if check_sprinkler_not_exists(sprinkler_id):
            timestamp = str(datetime.datetime.now())
            device_type = 'Sprinkler'

            print(f'sprinkler_id: {sprinkler_id}; timestamp: {timestamp}; device_type: {device_type}; lat: {lat}; '
                  f'long: {long}; min_devices_to_alarm: {sprinkler["min_devices_to_alarm"]}; ')

            sprinkler_info = put_sprinkler_info(sprinkler_id, timestamp, device_type, lat, long,
                                                sprinkler["min_devices_to_alarm"])
            print(sprinkler_info)

        for sen_id in range(1, sprinkler["devices_per_sprinkler"] + 1):
            temp_sensor_id = sprinkler['id'] + '_STS_' + str(sen_id)
            mois_sensor_id = sprinkler['id'] + '_SMS_' + str(sen_id)
            timestamp = str(datetime.datetime.now())
            temp_device_type = 'Temperature'
            mois_device_type = 'Moisture'

            print(f'sensor_id: {temp_sensor_id}; timestamp: {timestamp}; device_type: {temp_device_type}; '
                  f'sprinkler_id: {sprinkler_id}; ')
            sensor_info = put_sensor_info(temp_sensor_id, str(datetime.datetime.now()), temp_device_type, sprinkler_id)
            # print(sensor_info)

            print(f'sensor_id: {mois_sensor_id}; timestamp: {timestamp}; device_type: {mois_device_type}; '
                  f'sprinkler_id: {sprinkler_id}; ')
            sensor_info = put_sensor_info(mois_sensor_id, str(datetime.datetime.now()), mois_device_type, sprinkler_id)
            # print(sensor_info)


def load_config(file_name):
    print('Loading device configuration')
    f = open(file_name)
    config = json.loads(f.read())
    f.close()
    return config


def onboard_devices():
    print('Device Onboarding started...')
    # Load device config files for devices
    device_config = load_config("../resources/device_config.json")
    generate_and_populate_devices(device_config)


def check_sprinkler_not_exists(sprinkler_id):
    sprinkler_info = get_sprinkler_data(sprinkler_id)
    if sprinkler_info['Count'] > 0:
        var = sprinkler_info['Items'][0]['sprinkler_id']
        print(var)
        return False
    return True


onboard_devices()
# check_if_sprinkler_already_exists('sprinkler1')
