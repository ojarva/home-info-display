#!/usr/bin/bash

from multiprocessing import Process, Queue
import datetime
import json
import os
import redis
import subprocess
from setproctitle import setproctitle


def play_sound(sound_type):
    p = subprocess.Popen(["aplay", sound_type + ".wav"])
    p.wait()


class SoundReceiver:

    def __init__(self, redis_host, redis_port):
        self.r = redis.StrictRedis(host=redis_host, port=redis_port)

    def run(self):
        pubsub = self.r.pubsub(ignore_subscribe_messages=True)
        pubsub.subscribe("sound-notification")
        p = None
        current_source = None
        for message in pubsub.listen():
            print("%s: Got '%s'" % (datetime.datetime.now(), message))
            data = json.loads(message["data"])
            action = data.get("action", "play")
            source = data.get("source", "unknown")
            if action == "cancel" and current_source == source and p and p.is_alive():
                print("Terminating playing for source %s" % source)
                p.terminate()
                current_soure = None
            elif action == "play":
                sound_type = data.get("type", "normal")
                if p and not p.is_alive():
                    print("Playing %s" % sound_type)
                    current_source = data.get("source")
                    p = Process(target=play_sound, args=(sound_type,))
                    p.start()
                else:
                    print("Previous item is still playing - no action taken for %s" % data)
            print("%s: Finished '%s'" % (datetime.datetime.now(), message))

        pubsub.unsubscribe(channel)


def main():
    setproctitle("sound-receiver: run")
    redis_host = os.environ["REDIS_HOST"]
    redis_port = os.environ["REDIS_PORT"]
    sr = SoundReceiver(redis_host, redis_port)
    sr.run()

if __name__ == '__main__':
    main()
