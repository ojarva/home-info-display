from setproctitle import setproctitle
import json
import redis
import time
import datetime
import os


class IndoorQualityPublisher(object):
    def __init__(self, co2_file, redis_host, redis_port):
        self.co2_file = co2_file
        self.redis_instance = redis.StrictRedis(host=redis_host, port=redis_port)

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
            co2 = self.read_value(self.co2_file)
            influx_data = {
                "measurement": "indoor_air_quality",
                "time": now,
                "tags": {
                    "location": "display",
                },
                "fields": {}
            }
            if co2:
                self.redis_instance.setex("air-latest-co2", 300, co2)
                self.redis_instance.publish("home:broadcast:generic", json.dumps({"key": "indoor_co2", "content": {"value": co2}}))
                influx_data["fields"]["co2"] = co2

            if len(influx_data["fields"]) > 0:
                self.redis_instance.publish("influx-update-pubsub", json.dumps([influx_data]))
            time.sleep(15)


def main():
    setproctitle("indoor_quality_publisher: run")
    co2_file = os.environ["CO2_FILE"]
    redis_host = os.environ["REDIS_HOST"]
    redis_port = os.environ["REDIS_PORT"]
    iqp = IndoorQualityPublisher(co2_file, redis_host, redis_port)
    iqp.run()

if __name__ == '__main__':
    main()
