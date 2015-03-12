from setproctitle import setproctitle
import json
import local_settings
import paramiko
import re
import redis
import subprocess
import time

class UnifiStatusPublisher(object):
    stainfo_re = re.compile("(?P<timestamp>.{2,3})\[(?P<mac>.*)\] (?P<flags>.{3}) idle=(?P<idletime>[0-9 ]+)rssi=(?P<rssi>[0-9 ]+) (?P<bandwidth_in>[0-9 ]+)/(?P<bandwidth_out>[0-9 ]+)ccq=.*queued=(?P<tx>[0-9 ]+)/(?P<ret>[0-9 ]+)/(?P<queued>[0-9 ]+)rx=(?P<rx>[0-9 ]+)err=(?P<err>[0-9/ ]+)")

    def __init__(self):
        self.redis_instance = redis.StrictRedis()
        self.client = paramiko.client.SSHClient()
        self.client.load_system_host_keys()
        self.client.connect(local_settings.UNIFI_IP, username=local_settings.UNIFI_USERNAME, password=local_settings.UNIFI_PASSWORD)

    def poll_unifi_status(self):
        stdin, stdout, stderr = self.client.exec_command("stainfo -a")
        publish_data = {"devices": [], "stats": {}}
        for line in stdout:
            data = line.strip()
            if data.startswith("- showing"):
                # end of data row
                self.redis_instance.publish("home:broadcast:generic", json.dumps({"key": "unifi-status", "content": publish_data}))
                publish_data = {"devices": [], "stats": {}}

                continue
            if data.startswith("wifi"):
                # Wifi info line
                continue

            matched = self.stainfo_re.match(data)
            if data is None:
                print "Invalid data: %s" % data
                continue
            item_data = {}
            item_data["last_seen"] = matched.group("timestamp")
            item_data["mac"] = matched.group("mac")
            item_data["flags"] = matched.group("flags")
            item_data["idle"] = int(matched.group("idletime").strip())
            item_data["rssi"] = int(matched.group("rssi").strip())
            item_data["bandwidth_in"] = int(matched.group("bandwidth_in").strip())
            item_data["bandwidth_out"] = int(matched.group("bandwidth_out").strip())
            item_data["rx"] = int(matched.group("rx").strip())
            item_data["tx"] = int(matched.group("tx").strip())
            publish_data["devices"].append(item_data)

    def run(self):
        while True:
            self.poll_unifi_status()
            break
            time.sleep(1)

def main():
    setproctitle("unifi_status_publisher: run")
    usp = UnifiStatusPublisher()
    usp.run()

if __name__ == '__main__':
    main()
