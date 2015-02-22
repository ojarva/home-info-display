from setproctitle import setproctitle
import json
import local_settings
import manage_server_power
import redis
import subprocess
import time

class ServerPowerPublisher(object):
    def __init__(self):
        self.redis_instance = redis.StrictRedis()

        self.sp = manage_server_power.ServerPower(server_hostname=local_settings.SERVER_IP_ADDRESS, server_mac=local_settings.SERVER_MAC_ADDRESS, ssh_username=local_settings.SERVER_SSH_USERNAME, broadcast_ip=local_settings.SERVER_BROADCAST_IP)


    def check_server_power(self):
        status = "unknown"
        alive_status = self.sp.is_alive()
        if alive_status == manage_server_power.SERVER_UP:
            status = "running"
        elif alive_status == manage_server_power.SERVER_UP_NOT_RESPONDING:
            status = "not_responding"
        elif alive_status == manage_server_power.SERVER_DOWN:
            status = "down"
        self.redis_instance.publish("home:broadcast:generic", json.dumps({"key": "server_power", "content": {"status": status}}))

    def run(self):
        while True:
            self.check_server_power()
            time.sleep(1)

def main():
    setproctitle("server_power_publisher: run")
    spp = ServerPowerPublisher()
    spp.run()

if __name__ == '__main__':
    main()
