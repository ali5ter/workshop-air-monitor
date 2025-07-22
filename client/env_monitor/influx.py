# @file: influx.py
# @brief: InfluxDB client for storing environmental data
# @author: Alister Lewis-Bowen <alister@lewis-bowen.org>

import os
import logging
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

class INFLUX(object):

    def __init__(self, env_file='../server/influx_grafana_config.env'):

        # Load environment variables from .env file
        try:
            env_path = os.path.abspath(env_file)
            load_dotenv(dotenv_path=env_path)
            logging.debug(f"Loaded environment variables from {env_path}")
        except Exception as e:
            logging.error(f"Failed to load environment variables: {e}")
            raise

        # Assemble the InfluxDB connection parameters
        server_ip = os.getenv("SERVER_IP")
        port = os.getenv("INFLUXDB_PORT")
        if server_ip and port:
            self.url = f"http://{server_ip}:{port}"
        else:
            raise ValueError("Missing SERVER_IP or INFLUXDB_PORT environment variables")
        self.token = os.getenv("INFLUXDB_ADMIN_TOKEN")
        self.org = os.getenv("INFLUXDB_ORG")
        self.bucket = os.getenv("INFLUXDB_BUCKET")
        if not all([self.token, self.org, self.bucket]):
            raise ValueError("Missing INFLUXDB_ADMIN_TOKEN, INFLUXDB_ORG, or INFLUXDB_BUCKET environment variables")

        # Create client
        try:
            self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
            logging.info("Connected to InfluxDB")
        except Exception as e:
            logging.error(f"Error connecting to InfluxDB: {e}")
            raise

    def write_data(self, measurement: str, fields: dict, tags: dict = None):
        try:
            point = Point(measurement).time(None, WritePrecision.NS)

            if tags:
                for k, v in tags.items():
                    point = point.tag(k, v)

            for k, v in fields.items():
                point = point.field(k, v)

            self.write_api.write(bucket=self.bucket, record=point)
            logging.debug(f"Wrote data to InfluxDB: {fields}")
        except Exception as e:
            logging.error(f"Failed to write data to InfluxDB: {e}")

    def close(self):
        try:
            self.client.close()
            logging.info("Closed InfluxDB client")
        except Exception as e:
            logging.warning(f"Error closing InfluxDB client: {e}")