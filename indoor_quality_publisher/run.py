from local_settings import *
from setproctitle import setproctitle
from influxdb import InfluxDBClient
import influxdb.exceptions
import json
import redis
import time
import datetime

class IndoorQualityPublisher(object):
    def __init__(self):
        self.redis_instance = redis.StrictRedis()
        self.influx_client = InfluxDBClient("localhost", 8086, "root", "root", "home")

        try:
            self.influx_client.create_database("home")
        except influxdb.exceptions.InfluxDBClientError:
            pass

    @classmethod
    def read_value(cls, filename):
        try:
            value = float(open(filename).read())
            return value
        except IOError:
            return

    def run(self):
        while True:
            now = datetime.datetime.utcnow().isoformat() + "Z"
            temperature = self.read_value(TEMPERATURE_FILE)
            co2 = self.read_value(CO2_FILE)
            influx_data = {
                "measurement": "indoor_air_quality",
                "time": now,
                "tags": {
                    "location": "display",
                },
                "fields": {}
            }
            if co2:
                self.redis_instance.rpush("air-quality-co2", co2)
                self.redis_instance.publish("home:broadcast:generic", json.dumps({"key": "indoor_co2", "content": {"value": co2}}))
                influx_data["fields"]["co2"] = co2
            if temperature:
                self.redis_instance.rpush("air-quality-temperature", temperature)
                self.redis_instance.publish("home:broadcast:generic", json.dumps({"key": "indoor_temperature", "content": {"value": temperature}}))
                influx_data["fields"]["co2_temperature"] = temperature

            if len(influx_data["fields"]) > 0:
                self.redis_instance.publish("influx-update-pubsub", json.dumps(influx_data))
                self.influx_client.write_points([influx_data])
            time.sleep(15)

def main():
    setproctitle("indoor_quality_publisher: run")
    iqp = IndoorQualityPublisher()
    iqp.run()

if __name__ == '__main__':
    main()
