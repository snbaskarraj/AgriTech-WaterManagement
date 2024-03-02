import streamlit as st
import boto3
import pandas as pd
import matplotlib.pyplot as plt

# Initialize a DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='your-region')  # specify your AWS region


# Function to fetch data from a DynamoDB table
def fetch_data_from_dynamodb(table_name):
    table = dynamodb.Table(table_name)
    response = table.scan()
    items = response['Items']

    # Handling pagination
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response['Items'])

    return items


# Streamlit app layout
st.title('DynamoDB Data Visualization')

# Selecting a table to visualize
table_name = st.selectbox('Select a table to visualize', ['soil_sensor_info', 'sprinkler_info', 'weather_info'])

if st.button('Fetch and Visualize Data'):
    # Fetch data from DynamoDB
    data = fetch_data_from_dynamodb(table_name)

    # Convert to pandas DataFrame
    df = pd.DataFrame(data)

    # Example data processing (adjust according to your data)
    # Ensure 'timestamp' and 'some_metric' columns exist and are named appropriately
    if 'timestamp' in df.columns and 'some_metric' in df.columns:  # Replace 'some_metric' with a relevant column
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.sort_values(by='timestamp', inplace=True)

        # Plotting
        fig, ax = plt.subplots()
        ax.plot(df['timestamp'], df['datatype'])  # Adjust 'some_metric' accordingly
        ax.set_title(f'Trend for {table_name}')
        ax.set_xlabel('Timestamp')
        ax.set_ylabel('Value')
        plt.xticks(rotation=45)
        plt.tight_layout()

        st.pyplot(fig)
    else:
        st.write("The selected table does not have the necessary columns for this visualization.")

