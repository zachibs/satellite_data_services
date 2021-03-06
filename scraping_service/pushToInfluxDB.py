# Used this article to construct this script:
# https://www.influxdata.com/blog/getting-started-with-python-and-influxdb-v2-0/

# TODO need to write a function that takes a df and create Point objects from it

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
import socket
import pandas as pd
from generateFinalData import generate
from datetime import datetime


def push_to_db():
    # Get local ip

    # when used outside the container
    # hostname = socket.gethostname()
    # IP = f"{socket.gethostbyname(hostname)}:8086"

    # when used inside the container
    IP = "http://influxdb:8086"
    print(IP)

    # Connect to influxdb using the credentials in the docker-compose file
    client = InfluxDBClient(url=IP, token="123456789", org="influx")

    # creating APIs:
    write_api = client.write_api(write_options=SYNCHRONOUS)
    delete_api = client.delete_api()
    query_api = client.query_api()
    bucket_api = client.buckets_api()

    # creating and deleting a new bucket
    # bucket_api.delete_bucket(bucket_api.find_bucket_by_name("SATLLA-2B"))
    # bucket_api.create_bucket(bucket_name="SATLLA-2B")

    # generating the data
    generate()
    data = pd.read_csv("generatedCSVs/GeneratedData.csv")
    data.drop("Unnamed: 0", axis=1, inplace=True)
    three_hours_nanoseconds = 0
    # three_hours_nanoseconds = 10800000000000  # when used outside container
    data["timestamp"] = data["timestamp"].apply(
        lambda x: pd.to_datetime(x).value - three_hours_nanoseconds)
    data["battery_volts"] = data["battery_volts"].apply(
        lambda x: x/1000)
    first_row = data.iloc[0:1]  # capturing the latest telemetry
    first_row.set_index("timestamp", inplace=True)
    data.set_index("timestamp", inplace=True)

    # deleting former latest telemetry and writing the new latest
    start = "1970-01-01T00:00:00Z"
    stop = f"{datetime.now().date()}T23:59:00Z"
    delete_api.delete(start, stop, '_measurement="latest"', bucket="SATLLA-2B")
    write_api.write("SATLLA-2B", record=first_row, data_frame_measurement_name="latest",
                    data_frame_tag_columns=["msg_type"])

    # creating separate dataframes for each field

    columns_list = ["local_address", "sd_outbox", "msg_type", "msg_index", "battery_volts", "battery_current", "sns_ntc1",
                    "sns_ntc2", "destination", "msg_size", "msg_time", "msg_ack_req", "gps_month",
                    "gps_day", "gps_hour", "gps_min", "gps_lat", "gps_lng", "gps_alt", "gps_speed",
                    "gps_course", "gps_sat", "sns_gx", "sns_gy", "sns_gz", "sns_mx", "sns_my",
                    "sns_mz", "sns_bmp_temp_c", "battery_soc", "battery_health", "battery_full_capacity",
                    "battery_capacity", "battery_power", "sd_sent", "sd_rpi", "sd_files"]

    columns_list.remove("battery_volts")
    battery_volts = data.drop(columns_list, axis=1, inplace=False)
    columns_list.append("battery_volts")

    columns_list.remove("battery_current")
    battery_current = data.drop(columns_list, axis=1, inplace=False)
    columns_list.append("battery_current")

    columns_list.remove("sns_ntc1")
    sns_ntc1 = data.drop(columns_list, axis=1, inplace=False)
    columns_list.append("sns_ntc1")

    columns_list.remove("sns_ntc2")
    sns_ntc2 = data.drop(columns_list, axis=1, inplace=False)
    columns_list.append("sns_ntc2")

    long_data = data.dropna(inplace=False)

    columns_list.remove("sns_bmp_temp_c")
    sns_bmp_temp_c = long_data.drop(columns_list, axis=1, inplace=False)
    columns_list.append("sns_bmp_temp_c")

    columns_list.remove("sns_mx")
    sns_mx = long_data.drop(columns_list, axis=1, inplace=False)
    columns_list.append("sns_mx")

    columns_list.remove("sns_my")
    sns_my = long_data.drop(columns_list, axis=1, inplace=False)
    columns_list.append("sns_my")

    columns_list.remove("sns_mz")
    sns_mz = long_data.drop(columns_list, axis=1, inplace=False)
    columns_list.append("sns_mz")

    columns_list.remove("sns_gx")
    sns_gx = long_data.drop(columns_list, axis=1, inplace=False)
    columns_list.append("sns_gx")

    columns_list.remove("sns_gy")
    sns_gy = long_data.drop(columns_list, axis=1, inplace=False)
    columns_list.append("sns_gy")

    columns_list.remove("sns_gz")
    sns_gz = long_data.drop(columns_list, axis=1, inplace=False)
    columns_list.append("sns_gz")

    # writing in separate measurements:
    write_api.write("SATLLA-2B", record=battery_volts,
                    data_frame_measurement_name="battery_volts")
    write_api.write("SATLLA-2B", record=battery_current,
                    data_frame_measurement_name="battery_current")
    write_api.write("SATLLA-2B", record=sns_ntc1,
                    data_frame_measurement_name="sns_ntc1")
    write_api.write("SATLLA-2B", record=sns_ntc2,
                    data_frame_measurement_name="sns_ntc2")
    write_api.write("SATLLA-2B", record=sns_bmp_temp_c,
                    data_frame_measurement_name="sns_bmp_temp_c")
    write_api.write("SATLLA-2B", record=sns_mx,
                    data_frame_measurement_name="sns_mx")
    write_api.write("SATLLA-2B", record=sns_my,
                    data_frame_measurement_name="sns_my")
    write_api.write("SATLLA-2B", record=sns_mz,
                    data_frame_measurement_name="sns_mz")
    write_api.write("SATLLA-2B", record=sns_gx,
                    data_frame_measurement_name="sns_gx")
    write_api.write("SATLLA-2B", record=sns_gy,
                    data_frame_measurement_name="sns_gy")
    write_api.write("SATLLA-2B", record=sns_gz,
                    data_frame_measurement_name="sns_gz")

    # # Deprecated -------- Writing the data to the database
    # write_api.write("dataframe", record=data, data_frame_measurement_name="continuos_data",
    #                 data_frame_tag_columns=["msg_index"])

    client.close()
