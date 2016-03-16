from setproctitle import setproctitle
import datetime
import json
import os
import redis
import serial
import time


class IndoorAirQualitySerial:
    INPUT_MAP = {
        "14": "mq-3",
        "15": "mq-2",
        "16": "mq-9",
        "17": "aq",
        "20": "mq-5",
        "21": "hcho",
    }

    def __init__(self, serial_device, redis_host, redis_port):
        self.redis_instance = redis.StrictRedis(host=redis_host, port=redis_port)
        self.serial = serial.Serial(serial_device, 9600)

    def run(self):
        influx_fields = {}
        last_updated_at = time.time()
        while True:
            current_time = datetime.datetime.utcnow()
            line = self.serial.readline().strip()
            print("Received '%s'" % line)
            line = line.strip().split(":")
            if len(line) != 2:
                continue
            try:
                k = self.INPUT_MAP[line[0]]
            except KeyError:
                print("Invalid key: %s" % line[0])
                continue
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
                influx_fields = {}
                last_updated_at = time.time()


def main():
    setproctitle("indoor_air_quality - serial: run")
    serial_device = os.environ["SERIAL_DEVICE"]
    redis_host = os.environ["REDIS_HOST"]
    redis_port = os.environ["REDIS_PORT"]
    iqps = IndoorAirQualitySerial(serial_device, redis_host, redis_port)
    iqps.run()

if __name__ == '__main__':
    main()
