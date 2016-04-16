from setproctitle import setproctitle
import json
import os
import redis
import subprocess
import time


class DisplayControlConsumer(object):

    def __init__(self, redis_host, redis_port):
        self.redis_instance = redis.StrictRedis(host=redis_host, port=redis_port)
        self.env = {"DISPLAY": ":0"}

    def get_brightness(self):
        p = subprocess.Popen(["xrandr", "--verbose"],
                             env=self.env, stdout=subprocess.PIPE)
        (stdout, _) = p.communicate()
        for line in stdout.split("\n"):
            if "Brightness" in line:
                return float(line.strip().split(": ")[1])

    def set_brightness(self, brightness):
        p = subprocess.Popen(["xrandr", "--q1", "--output", "HDMI-0", "--brightness", brightness], env=self.env)
        p.wait()
        self.redis_instance.publish("home:broadcast:generic", json.dumps({"key": "display_brightness", "content": brightness}))

    def run(self):
        pubsub = self.redis_instance.pubsub(ignore_subscribe_messages=True)
        pubsub.subscribe("display-control-set-brightness")
        for _ in pubsub.listen():
            # Only poll redis after triggered with pubsub
            self.set_brightness(item["data"])


def main():
    setproctitle("display-control-consumer: run")
    redis_host = os.environ["REDIS_HOST"]
    redis_port = os.environ["REDIS_PORT"]
    dcc = DisplayControlConsumer(redis_host, redis_port)
    dcc.run()

if __name__ == '__main__':
    main()
