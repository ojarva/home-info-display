from influxdb import InfluxDBClient
import datetime
import json
import redis
import influxdb.exceptions
import requests.exceptions


class InfluxUpdateReceiver(object):

    def __init__(self):
        self.redis = redis.StrictRedis()
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
    iur = InfluxUpdateReceiver()
    iur.run()

if __name__ == '__main__':
    main()
