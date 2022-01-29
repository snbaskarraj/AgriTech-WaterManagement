import json


def lambda_handler(event, context):
    # TODO implement
    for e in event:
        if 'timestamp' in e:
            timestamp_rec = e['timestamp']
            timestamp_rec = timestamp_rec.replace(" ", "T")
            timestamp_rec = timestamp_rec + "Z"
            e['timestamp'] = timestamp_rec
    #       e['timestamp'] = timestamp_rec.isoformat()
    return event
