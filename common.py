import ttn_storage_api
import dateutil.parser
import pytz
from device_data import DEVICES


def load_data_by_device_id(app_name, api_key, window):
    """
    Take in the TTN API arguments and emit a dictionary keyed by device ID and a list of tuple
    (time, battery, temp, humidity)
    """
    results = ttn_storage_api.sensor_pull_storage(app_name, api_key, window, ttn_version=3)
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

