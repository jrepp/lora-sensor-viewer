#!/usr/bin/env python3

import json
import sys
import csv
import argparse
import ttn_storage_api

import common

parser = argparse.ArgumentParser(prog=__file__, description="export sensor data to csv format")
parser.add_argument("-n", "--app-name", help="TTN application name", required=True)
parser.add_argument("-k", "--api-key", help="TTN API key", required=True)
parser.add_argument("-w", "--window", help="TTN data window (24h, 48h)", default="24h")
args = parser.parse_args()

with open("sensor_export.csv", "w+") as output_file:
    writer = csv.writer(output_file)
    writer.writerow(["device_id", "datetime", "battery_mv", "temp_c", "humidity_pct"])
    for device_key, values in common.load_data_by_device_id(args.app_name, args.api_key, args.window).items():
        for v in values:
            # time, battery, temp, humidity
            writer.writerow([device_key,] + list(v))

