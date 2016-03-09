import datetime
import redis


class InfluxUpdateReceiver(object):

    def __init__(self):
        self.redis = redis.StrictRedis()
        self.current_filename = None
        self.current_file = None

    @classmethod
    def filename(cls):
        return "/var/log/influx-raw-log/updates-%s.log" % datetime.date.today()

    def run(self):
        pubsub = self.redis.pubsub(ignore_subscribe_messages=True)
        pubsub.subscribe("influx-update-pubsub")
        pubsub.subscribe("influx-update-logs-only-pubsub")
        for message in pubsub.listen():
            current_filename = self.filename()
            if self.current_filename != current_filename:
                if self.current_file:
                    self.current_file.close()
                self.current_filename = current_filename
                self.current_file = open(current_filename, "a")
            self.current_file.write(datetime.datetime.now(
            ).isoformat() + " " + message["data"] + "\n")
            self.current_file.flush()

        if self.current_file:
            self.current_file.close()
            self.current_file = None


def main():
    iur = InfluxUpdateReceiver()
    iur.run()

if __name__ == '__main__':
    main()
