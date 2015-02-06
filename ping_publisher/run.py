import time
import subprocess
from local_settings import *
import redis

redis_instance = redis.StrictRedis()

def iterate_all_destinations():

    times = []

    for dest in DESTINATIONS:
        # TODO: different parameters for Linux
        p = subprocess.Popen(["ping", "-c1", "-t2", dest], stdout=subprocess.PIPE)
        p.wait()
        (output, _) = p.communicate()
        if p.returncode != 0:
            continue
        output = output.split("\n")
        for line in output:
            if "bytes from" in line:
                line = line.split(" ")
                for item in line:
                    if item.startswith("time="):
                        item = item.split("=")
                        times.append(float(item[1]))

    message = None
    if len(times) == 0:
        message = "no_pings"
    else:
        message = min(times)
    redis_instance.publish("home:broadcast:ping", message)
    time.sleep(1)

if __name__ == '__main__':
    while True:
        iterate_all_destinations()
