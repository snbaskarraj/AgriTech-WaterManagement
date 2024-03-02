import boto3
from flask import Flask, render_template
import json
from decimal import Decimal

app = Flask(__name__)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')

# DynamoDB Tables
soil_sensor_table = dynamodb.Table('soil_sensor_info')
sprinkler_info_table = dynamodb.Table('sprinkler_info')
weather_info_table = dynamodb.Table('weather_info')

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)  # Convert Decimal to float for JSON serialization
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)

@app.route('/')
def dashboard():
    # Fetch data from DynamoDB tables
    soil_sensor_data = soil_sensor_table.scan()['Items']
    sprinkler_data = sprinkler_info_table.scan()['Items']
    weather_data = weather_info_table.scan()['Items']

    # Convert DynamoDB data to JSON, using DecimalEncoder to handle Decimal types
    soil_sensor_json = json.dumps(soil_sensor_data, cls=DecimalEncoder)
    sprinkler_json = json.dumps(sprinkler_data, cls=DecimalEncoder)
    weather_json = json.dumps(weather_data, cls=DecimalEncoder)

    # Pass the JSON strings to the frontend
    return render_template('dashboard.html', soil_sensor_data=soil_sensor_json,
                           sprinkler_data=sprinkler_json,
                           weather_data=weather_json)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
