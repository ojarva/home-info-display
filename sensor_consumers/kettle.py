from multiprocessing import Process, Queue
from utils import SensorConsumerBase
import datetime
import ikettle2
import json
import redis
import select
import subprocess
import time

def listen_kettle_commands(queue):
    r = redis.StrictRedis()
    pubsub = r.pubsub()
    pubsub.subscribe("kettle-commands")
    for item in pubsub.listen():
        print "Received %s" % item
        if isinstance(item, dict):
            if isinstance(item["data"], str):
                item = json.loads(item["data"])
                queue.put(item)

class Kettle:
    def __init__(self):
        self.r = redis.StrictRedis()
        self.latest_status = None
        self.temperatures = []
        self.sensor_base = SensorConsumerBase("indoor_air_quality")
        self.last_update_at = 0

    def add_temperature(self, temperature):
        if temperature > 101:
            return
        self.temperatures.append(temperature)
        if len(self.temperatures) > 5:
            self.temperatures = self.temperatures[-5:]
        return self.get_temperature_average()

    def get_temperature_average(self):
        if len(self.temperatures) > 0:
            return sum(self.temperatures) / len(self.temperatures)
        return None

    def run(self):
        commands_queue = Queue()

        p_commands = Process(target=listen_kettle_commands, args=(commands_queue,))
        p_commands.start()
        kettle = ikettle2.Kettle2("192.168.10.156")
        kettle.connect()
        while True:
            time.sleep(0.2)
            data = kettle.read()
            status_updated = False
            if len(data) > 0:
                for item in data:
                    if item["type"] == "status":
                        status_updated = True
                        self.latest_status = item["data"]
                        self.latest_status["temperature"] = self.add_temperature(self.latest_status["temperature"])
            if status_updated:
                self.r.setex("kettle-info", 60, json.dumps(self.latest_status))
                self.r.publish("home:broadcast:generic", json.dumps({"key": "kettle-info", "content": self.latest_status}))

                if time.time() - self.last_update_at > 10:
                    self.last_update_at = time.time()
                    self.sensor_base.insert_into_influx([{
                        "measurement": "kettle",
                        "time": datetime.datetime.utcnow().isoformat() + "Z",
                        "fields": {
                            "temperature": self.latest_status["temperature"],
                            "water_level": self.latest_status["water_level_raw"],
                            "present": self.latest_status["present"],
                            "status": self.latest_status["status"],
                        }
                    }])

            try:
                command = commands_queue.get(False)
            except:
                continue
            if command.get("on"):
                if self.latest_status is None:
                    print "Can't turn on - no status information available"
                    continue
                if not self.latest_status["present"]:
                    print "Can't turn on - kettle is not on the base"
                    continue
                if self.latest_status["water_level"] in ("empty", "too_low"):
                    print "Can't turn on - not enough water"
                    continue
                kettle.on(command.get("on", 100))
            elif command.get("off"):
                kettle.off()

def main():
    kettle = Kettle()
    kettle.run()

if __name__ == '__main__':
    main()
