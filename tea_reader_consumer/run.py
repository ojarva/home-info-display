from local_settings import BASE_URL
import datetime
import json
import redis
import requests
import requests.exceptions


class TeaReaderConsumer(object):

    def __init__(self):
        self.redis = redis.StrictRedis()

    def run(self):
        pubsub = self.redis.pubsub(ignore_subscribe_messages=True)
        pubsub.subscribe("tea-reader-pubsub")
        for message in pubsub.listen():
            try:
                data = json.loads(message["data"])
            except (ValueError, TypeError) as err:
                print "Failed to decode redis data: %s" % err
                continue
            resp = requests.get(BASE_URL + "tea/get/" + data["id"])
            print resp.content
            if resp.status_code != 200:
                print "Getting details for %s failed: %s" % (data["id"], resp.status_code)
                continue

            tag_data = resp.json()
            if tag_data["fields"]["boil_water"]:
                self.redis.publish("kettle-commands", json.dumps({"on": tag_data["fields"]["boil_water"]}))
                requests.post(BASE_URL + "tea/get/" + data["id"])


def main():
    runner = TeaReaderConsumer()
    runner.run()

if __name__ == '__main__':
    main()
