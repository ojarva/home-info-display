#!/usr/bin/bash
import datetime
import json
import redis
import subprocess

class SoundReceiver:
    def __init__(self):
        self.r = redis.StrictRedis()

    def run(self):
        pubsub = self.r.pubsub(ignore_subscribe_messages=True)
        pubsub.subscribe("sound-notification")
        for message in pubsub.listen():
            print "%s: Got '%s'" % (datetime.datetime.now(), message)
            data = json.loads(message["data"])
            sound_type = data.get("type", "normal")
            p = subprocess.Popen(["aplay", sound_type + ".wav"])
            p.wait()
            print "%s: Finished '%s'" % (datetime.datetime.now(), message)

        pubsub.unsubscribe(channel)


def main():
    sr = SoundReceiver()
    sr.run()

if __name__ == '__main__':
    main()
