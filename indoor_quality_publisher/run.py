from local_settings import *
from setproctitle import setproctitle
import json
import redis
import time

class IndoorQualityPublisher(object):
    def __init__(self):
        self.redis_instance = redis.StrictRedis()

    @classmethod
    def read_value(cls, filename):
        try:
            value = float(open(filename).read())
            return value
        except IOError:
            return

    def run(self):
        while True:
            temperature = self.read_value(TEMPERATURE_FILE)
            co2 = self.read_value(CO2_FILE)
            if co2:
                self.redis_instance.rpush("air-quality-co2", co2)
                self.redis_instance.publish("home:broadcast:generic", json.dumps({"key": "indoor_co2", "content": {"value": co2}}))
            if temperature:
                self.redis_instance.rpush("air-quality-temperature", temperature)
                self.redis_instance.publish("home:broadcast:generic", json.dumps({"key": "indoor_temperature", "content": {"value": temperature}}))

            time.sleep(15)

def main():
    setproctitle("indoor_quality_publisher: run")
    iqp = IndoorQualityPublisher()
    iqp.run()

if __name__ == '__main__':
    main()
