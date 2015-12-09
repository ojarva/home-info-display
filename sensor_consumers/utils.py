from local_settings import *
import datetime
import json
import redis
import requests

class SensorConsumerBase:
    def __init__(self):
        self.redis_instance = redis.StrictRedis()

    def subscribe(self, channel, callback):
        pubsub = self.redis_instance.pubsub(ignore_subscribe_messages=True)
        pubsub.subscribe(channel)
        for message in pubsub.listen():
            print "Got '%s'" % message
            data = json.loads(message["data"])
            if "timestamp" in data:
                data["timestamp"] = datetime.datetime.fromtimestamp(data["timestamp"])
            callback(data)

        pubsub.unsubscribe(channel)

    def update_notification(self, item_type, description, can_dismiss):
        resp = requests.post(BASE_URL + "notifications/create", data={"item_type": item_type, "description": description, "can_dismiss": can_dismiss})
        print "Creating %s (%s, %s): %s" % (item_type, description, can_dismiss, resp.status_code)

    def delete_notification(self, item_type):
        resp = requests.delete(BASE_URL + "notifications/delete/" + item_type)
        print "Deleting %s: %s" % (item_type, resp.status_code)

    def get_elapsed_time(self, timestamp):
        time_diff = datetime.datetime.now() - timestamp
        return self.format_elapsed_time(time_diff)

    def format_elapsed_time(self, delta):
        total_seconds = delta.total_seconds()
        if total_seconds < 60:
            return "<1min"
        if total_seconds > 86400:
            return "%svrk" % int(total_seconds / 86400)
        if total_seconds > 3600:
            return "%sh" % int(total_seconds / 3600)
        return "%smin" % int(total_seconds / 60)
