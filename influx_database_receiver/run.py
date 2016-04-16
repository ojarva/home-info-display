from influxdb import InfluxDBClient
import datetime
import influxdb.exceptions
import json
import os
import redis
import requests.exceptions
from setproctitle import setproctitle


class InfluxUpdateReceiver(object):

    def __init__(self, redis_host, redis_port):
        self.redis = redis.StrictRedis(host=redis_host, port=redis_port)
        self.influx = InfluxDBClient("localhost", 8086, "root", "root", "home")

    def run(self):
        pubsub = self.redis.pubsub(ignore_subscribe_messages=True)
        pubsub.subscribe("influx-update-pubsub")
        pubsub.subscribe("influx-update-influx-only-pubsub")
        for message in pubsub.listen():
            try:
                data = json.loads(message["data"])
            except (ValueError, TypeError) as err:
                print "Failed to decode influx data: %s" % err
                continue
            try:
                self.influx.write_points(data)
            except (influxdb.exceptions.InfluxDBClientError, requests.exceptions.ConnectionError) as err:
                print "Failed to update influx: %s" % err


def main():
    setproctitle("influx-database-receiver: run")
    redis_host = os.environ["REDIS_HOST"]
    redis_port = os.environ["REDIS_PORT"]
    iur = InfluxUpdateReceiver(redis_host, redis_port)
    iur.run()

if __name__ == '__main__':
    main()
