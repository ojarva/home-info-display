from local_settings import CO2_FILE
import json
import redis
import time


def fetch_indoor_quality():
    co2 = float(open(settings.CO2_FILE).read())
    return co2


def main():
    redis_instance = redis.StrictRedis()
    while True:
        co2 = fetch_indoor_quality()
        r.rpush("air-quality-co2", co2)
        redis_instance.publish("home:broadcast:generic", json.dumps({"key": "indoor_co2", "value": co2}))
        time.sleep(30)


if __name__ == '__main__':
    main()
