from setproctitle import setproctitle
import json
import paramiko
import redis
import time
import os


class DhcpLeasesPublisher(object):

    def __init__(self, server_ip, username, password, redis_host="localhost", redis_port=6379):
        self.redis_instance = redis.StrictRedis(host=redis_host, port=redis_port)
        self.client = paramiko.client.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(server_ip, username=username, password=password)

    def poll_dhcp_leases(self):
        _, stdout, _ = self.client.exec_command("cat /var/run/dhcpd.leases")
        publish_data = {"devices": {}, "stats": {}}
        item_data = {}
        for line in stdout:
            data = line.strip()
            if data.startswith("#"):
                # Skip comment lines
                continue
            if len(data) == 0:
                # Skip empty lines
                continue
            item_data["dynamic"] = True
            if data.startswith("lease "):
                if "mac" in item_data:
                    publish_data["devices"][item_data["mac"]] = item_data
                item_data = {}
                continue
            if data.startswith("binding state active"):
                item_data["active"] = True
            elif data.startswith("client-hostname"):
                item_data["hostname"] = data.split(
                    " ")[1].replace("\"", "").replace(";", "")
            elif data.startswith("hardware ethernet "):
                item_data["mac"] = data.split(" ")[2].replace(";", "")

        if "mac" in item_data:
            publish_data["devices"][item_data["mac"]] = item_data

        _, stdout, _ = self.client.exec_command("sudo cat /config/config.boot")
        hostname = ip_address = mac_address = None
        block_open = False
        for line in stdout:
            if "static-mapping " in line:
                block_open = True
                hostname = line.strip().split(" ")[1]
                continue
            if block_open:
                if "}" in line:
                    block_open = False
                    if hostname and ip_address and mac_address:
                        publish_data["devices"][mac_address] = {
                            "hostname": hostname, "ip": ip_address, "mac": mac_address}
                    hostname = ip_address = mac_address = None
                elif "ip-address " in line:
                    ip_address = line.strip().split(" ")[1]
                elif "mac-address " in line:
                    mac_address = line.strip().split(" ")[1]

        self.redis_instance.publish("home:broadcast:generic", json.dumps(
            {"key": "dhcp-leases", "content": publish_data}))

    def run(self):
        while True:
            self.poll_dhcp_leases()
            time.sleep(5)


def main():
    setproctitle("dhcp_leases_publisher: run")
    server_ip = os.environ["SERVER_IP"]
    username = os.environ["SERVER_USERNAME"]
    password = os.environ["SERVER_PASSWORD"]
    redis_host = os.environ["REDIS_HOST"]
    redis_port = os.environ["REDIS_PORT"]
    dlp = DhcpLeasesPublisher(server_ip, username, password, redis_host, redis_port)
    dlp.run()

if __name__ == '__main__':
    main()
