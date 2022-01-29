import boto3
import pandas as pd
import datetime
import pytz
import json

print('Loading function')

s3_client = boto3.client('s3')
iot_client = boto3.client('iot-data', region_name='us-east-1')

def lambda_handler(event, context):
   try:
       bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
       s3_file_name = event["Records"][0]["s3"]["object"]["key"]
       csvfile = s3_client.get_object(Bucket=bucket_name, Key=s3_file_name)
       # read csv into pandas df
       df = pd.read_csv(csvfile['Body'])
       # Drop timestamp column
       df.drop('timestamp',inplace=True,axis=1)
       # Drop __dt column
       df.drop('__dt',inplace=True,axis=1)
       # compute mean value per device_id. datatype is unique per device_id
       agg_df = df.groupby(['device_id','datatype'], as_index=False)['value'].mean()
       # debug prints
       print(df.head())
       print(agg_df.head())
       #per_dev_dict = agg_df.to_dict(orient='records')
       #print(per_dev_dict)
       # for each device_id (row in agg_df), publish message to iot
       message = {}
       for k, row in agg_df.iterrows():
            timestamp_tobj = datetime.datetime.now()
            timestamp_utc = timestamp_tobj.astimezone(pytz.UTC)
            timestamp = timestamp_utc.strftime('%Y-%m-%d %H:%M:%S')
            message['timestamp'] = timestamp
            message['value'] = round(row["value"],2)
            message['device_id'] = row["device_id"]
            message['datatype'] = row["datatype"]
            messageJson = json.dumps(message)
            print(messageJson)
            # Change topic, qos and payload
            iot_client.publish(
                topic='iot/agritech_aggr',
                qos=1,
                payload=messageJson)
   except Exception as err:
      print(err)
