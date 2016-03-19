import datetime
import os
import redis


class InfluxUpdateReceiver(object):

    def __init__(self, redis_host, redis_port):
        self.redis = redis.StrictRedis(host=redis_host, port=redis_port)
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
    setproctitle("influx-logger-receiver: run")
    redis_host = os.environ["REDIS_HOST"]
    redis_port = os.environ["REDIS_PORT"]
    iur = InfluxUpdateReceiver(redis_host, redis_port)
    iur.run()

if __name__ == '__main__':
    main()
