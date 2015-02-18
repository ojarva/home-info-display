from local_settings import *
from setproctitle import setproctitle
import json
import re
import redis
import subprocess
import time

class PingRunner(object):
    PARSER = re.compile(".*: \[([0-9]+)\], .*bytes, ([0-9\.]+) ms.*")

    def __init__(self):
        self.redis_instance = redis.StrictRedis()
        self.counter = 0
        self.current_responses = []

    @classmethod
    def parse_ping_output(cls, line):
        match = cls.PARSER.match(line)
        if match is None:
            return
        counter = match.group(1)
        response = float(match.group(2))
        return (counter, response)

    def run(self):
        cmd = ["fping", "-l", "-e"]
        cmd += DESTINATIONS
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=1)
        for line in iter(p.stdout.readline, b''):
            (counter, response) = self.parse_ping_output(line)
            self.current_responses.append(response)
            if counter != self.counter:
                if len(self.current_responses) == 0:
                    message = "no_pings"
                else:
                    message = min(self.current_responses)
                self.current_responses = []
                self.counter = counter
                print "broadcasting", message
                self.redis_instance.publish("home:broadcast:generic", json.dumps({"key": "ping", "content": message}))

        p.communicate()

def main():
    setproctitle("ping_publisher: run")
    pr = PingRunner()
    pr.run()

if __name__ == '__main__':
    main()
