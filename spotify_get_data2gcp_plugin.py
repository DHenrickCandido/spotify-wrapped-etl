import sqlalchemy
import pandas as pd 
from sqlalchemy.orm import sessionmaker
import requests
import json
import pytz
from google.cloud import storage
from google.oauth2.service_account import Credentials

from datetime import datetime
import datetime
import sqlite3
import json
import pytz
import uuid
import logging

import pandas as pd
# from datetime import datetime
from google.cloud import storage
from flask import Response



# from infrastructure import check_json_schema, get_json_schema_from_gcs
# from authorization import has_authorization

# from parser_config import ConfigParser
# from monitoring import MonitoringApiErrors

TOKEN = "BQBjOSfywA2jvlQvBtOVnG_JS59GhW12v78r_XkzRnmXF2d-5qmAoTi9YMZZhvV7QWCcM3_5HUUAFHyn0d5n5S3Rz6Qdwm7VueI7sgKcXGRkJ3pas3KIYyyqfQFUHvm9R1TruEBht64J3Is4lED9goC5D-Bv9oWcHQv-GEx0TMfil8vAVByKAQDmbwtBo6c20E4jPTw0DA"
creds = Credentials.from_service_account_file("/home/kitinclusivotpta/spotify-wrapped-377220-112f18f655f4.json")
client = storage.Client(credentials=creds, project="spotify-wrapped")
bucket = client.bucket("spotify-raw")


def create_dt_insercao():
    insertion_date = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
    insertion_date = insertion_date.astimezone(pytz.timezone("America/Sao_Paulo"))
    return str(insertion_date)[:26]  # cut out the -3:00 timezone information

def process_payload(payload_to_process):
    dt_insercao = create_dt_insercao()
    df = pd.DataFrame()
    df = df.assign(payload=payload_to_process)
    df['played_at'] = df['payload'].map(lambda x: x['played_at'])
    df['context'] = df['payload'].map(lambda x: x['context'])
    df['partition'] = dt_insercao[:13]
    return df
    
def create_dt_insercao():
    insertion_date = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
    insertion_date = insertion_date.astimezone(pytz.timezone("America/Sao_Paulo"))
    return str(insertion_date)[:26]  # cut out the -3:00 timezone information

if __name__ == "__main__":

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {token}".format(token=TOKEN)
    }

    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)
    yesterday_unix_timestamp = int(yesterday.timestamp()) * 1000

    # r = requests.get('https://api.spotify.com/v1/me/player/recently-played?limit=200&after={time}'.format(time=yesterday_unix_timestamp), headers = headers)
    r = requests.get('https://api.spotify.com/v1/me/player/recently-played?limit=50'.format(time=yesterday_unix_timestamp), headers = headers)

    data = r.json()


    items = data["items"]

    # print(len(items))
    # print(payloads)

    payload_to_process = items

    df = process_payload(payload_to_process)
    parts = df['partition'].drop_duplicates().to_list()

    table_name = "songs-raw"

    for part in parts:
        year_part = part[:4]
        month_part = part[5:7]
        day_part = part[8:10]
        hour_part = part[11:13]
        blob_name = f'{table_name}/"test"'
        bucket.blob(blob_name).upload_from_string(df.to_json(orient='records', lines=True), 'application/json')

    response_text = {'statusCode': 201, 'body': 'Created'}

    logging.info("Saved to bucket")