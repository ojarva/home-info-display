import redis
import serial
import time
import datetime
from setproctitle import setproctitle
from local_settings import *
from influxdb import InfluxDBClient
import influxdb.exceptions

class IndoorAirQualitySerial:
    def __init__(self):
        self.redis_instance = redis.StrictRedis()
        self.serial = serial.Serial(SERIAL_DEVICE, 9600)
        self.influx_client = InfluxDBClient("localhost", 8086, "root", "root", "home")

        try:
            self.influx_client.create_database("home")
        except influxdb.exceptions.InfluxDBClientError:
            pass

    def run(self):
        influx_fields = {}
        last_updated_at = time.time()
        while True:
            current_time = datetime.datetime.utcnow()
            line = self.serial.readline().strip()
            print "Received '%s'" % line
            line = line.strip().split(":")
            if len(line) != 2:
                continue
            try:
                k = INPUT_MAP[line[0]]
            except KeyError:
                print "Invalid key: %s" % line[0]
                continue
            self.redis_instance.rpush("air-quality-%s" % k, line[1])
            influx_fields[k] = round(float(line[1]), 1)
            if time.time() - last_updated_at > 10:
                influx_data = [
                    {
                        "measurement": "gas_sensors",
                        "tags": {
                            "location": "display",
                        },
                        "time": current_time.isoformat() + "Z",
                        "fields": influx_fields
                    }
                ]
                self.redis_instance.publish("influx-update-pubsub", json.dumps(influx_data))
                self.influx_client.write_points(influx_data)
                influx_fields = {}
                last_updated_at = time.time()

def main():
    setproctitle("indoor_air_quality - serial: run")
    iqps = IndoorAirQualitySerial()
    iqps.run()

if __name__ == '__main__':
    main()
