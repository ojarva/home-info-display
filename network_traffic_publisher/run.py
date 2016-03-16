from setproctitle import setproctitle
import json
import local_settings
import redis
import time
import nettraffic
import datetime
import pprint


class NetworkStatusPublisher(object):

    def __init__(self, gw_ip, gw_port, gw_community, redis_host, redis_port):
        self.redis_instance = redis.StrictRedis(host=redis_host, port=redis_port)
        self.stats = nettraffic.CalcStats()
        self.traffic = nettraffic.GetNetworkStats(gw_ip, gw_port, gw_community)

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
                if item["descr"] == "eth0":  # internet
                    self.redis_instance.publish("home:broadcast:generic", json.dumps(
                        {"key": "internet-speed", "content": {"internet": {"speed_in": item["speed_in"], "speed_out": item["speed_out"]}}}))
                    influx_data = [{
                        "measurement": "bandwidth_usage",
                        "tags": {
                            "source": "edgerouter",
                        },
                        "time": datetime.datetime.utcnow().isoformat() + "Z",
                        "fields": {
                            "speed_in": int(item["speed_in"]),
                            "speed_out": int(item["speed_out"]),
                        }
                    }]
                    self.redis_instance.publish("influx-update-pubsub", json.dumps(influx_data))
                    break  # no need to continue loop


def main():
    setproctitle("network_traffic_publisher: run")
    gw_ip = os.environ["GW_IP"]
    gw_port = os.environ["GW_PORT"]
    gw_community = os.environ["GW_COMMUNITY"]
    redis_host = os.environ["REDIS_HOST"]
    redis_port = os.environ["REDIS_PORT"]
    ntp = NetworkStatusPublisher(gw_ip, gw_port, gw_community, redis_host, redis_port)
    ntp.run()

if __name__ == '__main__':
    main()
