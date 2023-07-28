#!/usr/bin/env python3
import ttn_storage_api
import json
import sys
import dateutil.parser
import streamlit as st
import pandas as pd
import numpy as np
import pytz

APP = st.secrets.ttn.app_name
KEY = st.secrets.ttn.api_key
WINDOW = '24h'

DEVICES = {
'eui-0080e115000752b1': 'E5-01',
'eui-0080e11500075243': 'E5-07',
'eui-0080e115003e014c': 'E5-02',
'eui-0080e1150017bb73': 'E5-04',
'eui-0080e1150503ea3e': 'E5-05',
'eui-0080e115000751b8': 'E5-06',
'eui-0080e1150503eea5': 'E5-10',
'eui-0080e1150007502d': 'E5-09',
'eui-0080e115000753a5': 'E5-08',
'eui-0080e1150503e9c8': 'E5-11',
}

st.title('Sensor POC')


@st.cache_data
def load_data(window):
    results = ttn_storage_api.sensor_pull_storage(APP, KEY, window, ttn_version=3)
    by_id = dict()
    for r in results:
        result_frag = r.get('result')
        if result_frag is None:
            raise Exception(f"Unexpected result {r}")
        timestamp = dateutil.parser.isoparse(result_frag['uplink_message']['received_at'])
        local_time = timestamp.astimezone(pytz.timezone("US/Pacific"))
        decoded_frag = result_frag['uplink_message']['decoded_payload']
        temp_c = decoded_frag['temp_c']
        if temp_c & 0x8000:
            temp_c = -0x10000 + temp_c
        humidity_pct = decoded_frag['humidity_pct']
        battery_mv = decoded_frag['battery_mv']
        if not temp_c:
            continue
        id = result_frag['end_device_ids']['device_id']
        key = f"{DEVICES[id]} ({id})"
        values = by_id.setdefault(key, list())
        values.append((local_time, battery_mv, temp_c, humidity_pct))
    return by_id


text_status = st.text('Loading data...')
by_id_data = load_data(st.selectbox('Select time window', ['24h', '48h', '72h']))
text_status.text('Data loaded')



for key, values in by_id_data.items():
    st.subheader(f"{key}")
    st.text(f"Date range: {values[0][0]} to {values[-1][0]}")
    chart_data = pd.DataFrame(values, columns=['datetime', 'battery_mv', 'temp_c', 'humidity_pct'])
    #st.write(chart_data)
    temp, hum, bat, data = st.tabs(['Temp (C)', 'Humidity%', 'Battery(mv)', 'Data'])
    bat.line_chart(x='datetime', y='battery_mv', data=chart_data)
    temp.line_chart(x='datetime', y='temp_c', data=chart_data)
    hum.line_chart(x='datetime', y='humidity_pct', data=chart_data)
    data.write(chart_data)
