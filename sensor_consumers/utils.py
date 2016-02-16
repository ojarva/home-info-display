from influxdb import InfluxDBClient
from local_settings import *
import datetime
import influxdb.exceptions
import json
import redis
import requests


class NotificationConfig(object):
    def __init__(self, notification, config):
        self.config = config
        self.notification = notification
        self.data = {}
        for level in ("normal", "high", "urgent"):
            self.data[level] = {}
            self.deactivate(level)
        self.current_notification = None

    def escalated(self, from_level, to_level):
        self.data[to_level]["escalated"] = True
        self.data[to_level]["triggered-since"] = self.data[from_level]["active-since"]
        self.data[to_level]["current-active"] = True
        if not self.data[to_level]["active-since"]:
            self.data[to_level]["active-since"] = datetime.datetime.now()

    def activate(self, level):
        self.data[level]["current-active"] = True
        if not self.data[level]["active-since"]:
            self.data[level]["active-since"] = datetime.datetime.now()

    def deactivate(self, level):
        self.data[level]["current-active"] = False
        self.data[level]["escalated"] = False
        self.data[level]["active-since"] = None
        self.data[level]["triggered-since"] = None
        self.data[level]["sound-played"] = False


class SensorConsumerBase(object):
    def __init__(self, influx_database=None):
        self.redis_instance = redis.StrictRedis()
        self.notification_data = None
        if influx_database:
            self.influx_client = InfluxDBClient("localhost", 8086, "root", "root", influx_database)
            try:
                self.influx_client.create_database(influx_database)
            except influxdb.exceptions.InfluxDBClientError:
                pass
            self.influx_database = influx_database
        else:
            influx_database = None

    def subscribe(self, channel, callback):
        pubsub = self.redis_instance.pubsub(ignore_subscribe_messages=True)
        pubsub.subscribe(channel)
        for message in pubsub.listen():
            print "Got '%s'" % message
            data = json.loads(message["data"])
            if "timestamp" in data:
                timestamp = data["timestamp"]
                data["timestamp"] = datetime.datetime.fromtimestamp(timestamp)
                data["utctimestamp"] = datetime.datetime.utcfromtimestamp(timestamp)
            callback(data)
        pubsub.unsubscribe(channel)

    def insert_into_influx(self, data):
        if not self.influx_database:
            raise ValueError("Influx is not initialized")
        self.influx_client.write_points(data)

    def update_notification_from_dict(self, **kwargs):
        return self.update_notification(kwargs["notification"], kwargs["message"], kwargs["user_dismissable"], **kwargs)

    def update_notification(self, item_type, description, can_dismiss, **kwargs):
        level = kwargs.get("level", "normal")
        elapsed_since = kwargs.get("elapsed_since")
        from_now_timestamp = kwargs.get("from_now_timestamp")
        if elapsed_since:
            elapsed_since = elapsed_since.isoformat()
        if from_now_timestamp:
            from_now_timestamp = from_now_timestamp.isoformat()
        resp = requests.post(BASE_URL + "notifications/create", data={"item_type": item_type, "description": description, "can_dismiss": can_dismiss, "elapsed_since": elapsed_since, "from_now_timestamp": from_now_timestamp, "level": level})
        print "Creating %s (%s, %s): %s - %s, args=%s" % (item_type, description, can_dismiss, resp.status_code, resp.content, kwargs)

    def play_sound(self, sound):
        print "Playing sound: {}".format(sound)
        self.redis_instance.publish("sound-notification", json.dumps({"type": sound, "timestamp": str(datetime.datetime.now())}))

    def delete_notification(self, item_type):
        resp = requests.delete(BASE_URL + "notifications/delete/" + item_type)
        print "Deleting %s: %s" % (item_type, resp.status_code)

    def get_elapsed_time(self, timestamp):
        time_diff = datetime.datetime.now() - timestamp
        return self.format_elapsed_time(time_diff)

    def initialize_notifications(self, notification_config):
        self.notification_data = {}
        for notification, config in notification_config.items():
            self.notification_data[notification] = NotificationConfig(notification, config)
            self.delete_notification(config["notification"])

    def check_notifications(self, data):
        notification_levels = ('normal', 'high', 'urgent')
        for notification, notification_config in self.notification_data.items():
            if notification not in data:
                continue

            notification_data = notification_config.data
            config = notification_config.config
            point = data[notification]
            earlier_active = False
            for i, level in enumerate(notification_levels):
                if level not in config:
                    continue
                alarm_matches = False
                if "gt" in config[level] and point > config[level]["gt"]:
                    alarm_matches = True
                if "lt" in config[level] and point < config[level]["lt"]:
                    alarm_matches = True
                if "bool" in config[level] and point == config[level]["bool"]:
                    alarm_matches = True
                if alarm_matches:
                    if not notification_data[level]["triggered-since"]:
                        notification_data[level]["triggered-since"] = datetime.datetime.now()
                    if "delay" in config[level]:
                        if datetime.datetime.now() - notification_data[level]["triggered-since"] > config[level]["delay"]:
                            notification_config.activate(level)
                            earlier_active = True
                        else:
                            print "Activating {level} is delayed".format(level=level)
                    else:
                        notification_config.activate(level)
                        earlier_active = True
                else:
                    # check whether previous level is escalated or triggered
                    if earlier_active:
                        # previous level is currently active -> keep this active as well
                        continue
                    notification_data[level]["active-since"] = None
                    notification_data[level]["current-active"] = False
                    notification_data[level]["triggered-since"] = None
                    earlier_active = False

            # Check escalations
            for i, level in enumerate(notification_levels):
                if level not in config:
                    continue

                if notification_data[level]["current-active"]:
                    if "escalate" in config[level]:
                        time_diff = datetime.datetime.now() - notification_data[level]["active-since"]
                        print "Escalation: time_diff={time_diff}, escalate={escalate}".format(time_diff=time_diff, escalate=config[level]["escalate"])
                        if time_diff > config[level]["escalate"]:
                            next_level = notification_levels[i + 1]
                            print "Escalating {from_level} to {to_level}".format(from_level=level, to_level=next_level)
                            notification_config.escalated(level, next_level)
                            continue

            # Update notifications and play sounds
            for i, level in enumerate(reversed(notification_levels)):
                if level not in config:
                    continue
                if notification_data[level]["current-active"]:
                    # update notification
                    if "message" in config[level]:
                        message = config[level]["message"]
                    else:
                        message = config["message"]
                    message_level = level
                    if level == "urgent":  # TODO
                        print "Level is urgent -> convert to high"
                        message_level = "high"
                    notification_meta = {"level": message_level, "message": message.format(value=point), "user_dismissable": False, "elapsed_since": notification_data[level]["triggered-since"], "notification": notification_config.notification}
                    if notification_config.current_notification != notification_meta:
                        notification_config.current_notification = notification_meta
                        self.update_notification_from_dict(**notification_meta)

                    # check sounds
                    if "sound" in config[level]:
                        time_diff = datetime.datetime.now() - notification_data[level]["active-since"]
                        print "Sound: time_diff={}".format(time_diff)
                        if time_diff > config[level]["sound"] and not notification_data[level]["sound-played"]:
                            notification_data[level]["sound-played"] = True
                            print "Playing sound triggered by {} - {}".format(notification_config.notification, level)
                            self.play_sound("finished")
                    break
            else:
                # no break executed - no notification is there.
                if notification_config.current_notification:
                    # delete notification
                    self.delete_notification(notification_config.notification)
                    notification_config.current_notification = None

    @classmethod
    def format_timedelta(cls, timedelta):
        """ Strip out microseconds """
        return datetime.timedelta(seconds=int(timedelta.total_seconds()))

    def format_elapsed_time(self, delta):
        total_seconds = delta.total_seconds()
        if total_seconds < 60:
            return "<1min"
        if total_seconds > 86400:
            return "%svrk" % int(total_seconds / 86400)
        if total_seconds > 3600:
            return "%sh" % int(total_seconds / 3600)
        return "%smin" % int(total_seconds / 60)
