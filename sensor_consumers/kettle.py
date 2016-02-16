from multiprocessing import Process, Queue
from utils import SensorConsumerBase
import datetime
import ikettle2
import json
import redis
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


class Kettle(SensorConsumerBase):
    def __init__(self):
        SensorConsumerBase.__init__(self, "indoor_air_quality")
        self.r = redis.StrictRedis()
        self.latest_status = None
        self.temperatures = []
        self.last_update_at = 0
        self.boil_to = None
        self.boiled_at = None
        self.eta = []
        self.kettle_dialog_visible = False
        self.delete_notification("kettle")
        self.kettle = None

    def add_temperature(self, timestamp, temperature):
        if temperature > 101:
            return
        self.temperatures.append((timestamp, temperature))
        self.temperatures = self.temperatures[-10:]
        return self.get_temperature_average()

    def get_temperature_average(self):
        if len(self.temperatures) > 0:
            temperatures = [a[1] for a in self.temperatures[-3:]]
            return sum(temperatures) / len(temperatures)
        return None

    def get_eta(self):
        if len(self.temperatures) < 3:
            return None
        if self.boil_to is None:
            return
        delta_per_second = None
        latest_timestamp, latest_temperature = self.temperatures[-1]
        for timestamp, temperature in reversed(self.temperatures[-5:-1]):
            if latest_timestamp - timestamp > datetime.timedelta(seconds=5):
                delta_per_second = float(latest_temperature - temperature) / (latest_timestamp - timestamp).total_seconds()
                break
        if delta_per_second is None or delta_per_second < 0.1 or delta_per_second > 2:
            return None

        diff = self.boil_to - latest_temperature
        if diff < 0:
            print "diff is %s" % diff
            return None
        eta = diff * delta_per_second
        if eta > 300:
            print "eta is %s" % eta
            return None
        self.eta.append(eta)
        self.eta = self.eta[-5:]
        return int(round(sum(self.eta) / len(self.eta)))

    def run(self):
        commands_queue = Queue()

        p_commands = Process(target=listen_kettle_commands, args=(commands_queue,))
        p_commands.start()
        self.kettle = ikettle2.Kettle2("192.168.10.156")
        self.kettle.connect()
        while True:
            time.sleep(0.2)
            data = self.kettle.read()
            status_updated = False
            if len(data) > 0:
                for item in data:
                    if item["type"] == "status":
                        status_updated = True
                        self.latest_status = item["data"]
                        self.latest_status["temperature"] = self.add_temperature(datetime.datetime.now(), self.latest_status["temperature"])
            if status_updated:
                self.r.setex("kettle-info", 60, json.dumps(self.latest_status))
                self.r.publish("home:broadcast:generic", json.dumps({"key": "kettle-info", "content": self.latest_status}))

                if self.latest_status["status"] == "boiling" and self.boil_to:
                    self.set_boiling_message()
                else:
                    self.eta = []
                    if self.latest_status["present"] and self.boiled_at and datetime.datetime.now() - self.boiled_at < datetime.timedelta(seconds=30):
                        self.update_notification("kettle", "Vesi valmis ({}&deg;C -&gt; {}&deg;C)".format(self.latest_status["temperature"], self.boil_to), False)
                        self.kettle_dialog_visible = True
                    else:
                        self.boiled_at = None
                        if self.kettle_dialog_visible:
                            self.delete_notification("kettle")
                            self.kettle_dialog_visible = False
                        self.boil_to = None

                if time.time() - self.last_update_at > 10:
                    self.push_to_influxdb(self.latest_status)

            try:
                command = commands_queue.get(False)
            except:
                continue
            self.process_command(command)

    def set_boiling_message(self):
        eta = self.get_eta()
        if eta is None:
            eta = "?"
        self.update_notification("kettle", "Vesi {current_temperature}&deg;C -&gt; {destination_temperature}&deg;C, ETA {eta}s".format(current_temperature=self.latest_status["temperature"], destination_temperature=self.boil_to, eta=eta), False)
        self.kettle_dialog_visible = True
        self.boiled_at = datetime.datetime.now()

    def push_to_influxdb(self, latest_status):
        water_level = latest_status["water_level"]
        if water_level:
            water_level = int(water_level * 100)
        self.last_update_at = time.time()
        self.insert_into_influx([{
            "measurement": "kettle",
            "time": datetime.datetime.utcnow().isoformat() + "Z",
            "fields": {
                "temperature": latest_status["temperature"],
                "water_level": latest_status["water_level_raw"],
                "water_level_percent": water_level,
                "present": latest_status["present"],
                "status": latest_status["status"],
            }
        }])

    def process_command(self, command):
        if command.get("on"):
            if self.latest_status is None:
                print "Can't turn on - no status information available"
                return
            if not self.latest_status["present"]:
                print "Can't turn on - kettle is not on the base"
                return
            if self.latest_status["water_level"] < 0.1:
                print "Can't turn on - not enough water"
                return
            destination_temperature = command.get("on", 100)
            self.boil_to = destination_temperature
            self.kettle.on(destination_temperature)
        elif command.get("off"):
            self.boiled_at = None
            self.kettle.off()


def main():
    kettle = Kettle()
    kettle.run()

if __name__ == '__main__':
    main()
