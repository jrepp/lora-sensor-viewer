#!/usr/bin/env python3
import ttn_storage_api
import json
import sys
import dateutil.parser
import streamlit as st
import pandas as pd
import numpy as np
import pytz
import common

st.title('Sensor POC')


@st.cache_data
def load_data(window):
    """Load data backed by cache"""
    return common.load_data_by_device_id(st.secrets.ttn.app_name, st.secrets.ttn.api_key, window)


text_status = st.text('Loading data...')
f_or_c = st.selectbox('Units', ['Celsius', 'Fahrenheit'])
by_id_data = load_data(st.selectbox('Select time window', ['24h', '48h', '72h']))
text_status.text('Data loaded')

# Create a per sensor graph with tabs for individual data plots
for key, values in by_id_data.items():
    st.subheader(f"{key}")
    st.text(f"Date range: {values[0][0]} to {values[-1][0]}")
    chart_data = pd.DataFrame(values, columns=['datetime', 'battery_mv', 'temp_c', 'humidity_pct'])
    if f_or_c == 'Fahrenheit':
        temp_label = 'Temp (F)'
        temp_col = 'temp_f'
        chart_data[temp_col] = chart_data.apply(lambda row: (row[2] * 9/5) + 32, axis=1)
    else:
        temp_label = 'Temp (C)'
        temp_col = 'temp_c'

    temp, hum, bat, data = st.tabs(['Temp (C)', 'Humidity%', 'Battery(mv)', 'Data'])
    bat.line_chart(x='datetime', y='battery_mv', data=chart_data)
    temp.line_chart(x='datetime', y=temp_col, data=chart_data)
    hum.line_chart(x='datetime', y='humidity_pct', data=chart_data)
    data.write(chart_data)
