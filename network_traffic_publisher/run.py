from setproctitle import setproctitle
import json
import local_settings
import redis
import time
import nettraffic
import pprint

class NetworkStatusPublisher(object):

    def __init__(self):
        self.redis_instance = redis.StrictRedis()
        self.stats = nettraffic.CalcStats()
        self.traffic = nettraffic.GetNetworkStats(local_settings.GW_IP, local_settings.GW_PORT, local_settings.GW_COMMUNITY)

    def get_stats(self):
        return self.traffic.get_stats()


    def run(self):
        stats = []
        while True:
            time.sleep(5)
            stats.append(self.get_stats())
            if len(stats) < 2:
                continue
            stats = stats[-2:]
            diff = self.stats.diff_stats(stats[0], stats[1])

            for _, item in diff.items():
                item_key = None
                if item["descr"] == "eth1": # internet
                    self.redis_instance.publish("home:broadcast:generic", json.dumps({"key": "internet-speed", "content": {"internet": {"speed_in": item["speed_in"], "speed_out": item["speed_out"]}}}))
                    break # no need to continue loop

def main():
    setproctitle("network_traffic_publisher: run")
    ntp = NetworkStatusPublisher()
    ntp.run()

if __name__ == '__main__':
    main()
