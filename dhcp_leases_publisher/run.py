from setproctitle import setproctitle
import json
import local_settings
import paramiko
import re
import redis
import subprocess
import time


class DhcpLeasesPublisher(object):

    def __init__(self):
        self.redis_instance = redis.StrictRedis()
        self.client = paramiko.client.SSHClient()
        self.client.load_system_host_keys()
        self.client.connect(local_settings.DHCP_SERVER_IP, username=local_settings.DHCP_SERVER_USERNAME, password=local_settings.DHCP_SERVER_PASSWORD)

    def poll_dhcp_leases(self):
        stdin, stdout, stderr = self.client.exec_command("cat /var/run/dhcpd.leases")
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
                item_data["hostname"] = data.split(" ")[1].replace("\"", "").replace(";", "")
            elif data.startswith("hardware ethernet "):
                item_data["mac"] = data.split(" ")[2].replace(";", "")

        if "mac" in item_data:
            publish_data["devices"][item_data["mac"]] = item_data

        stdin, stdout, stderr = self.client.exec_command("sudo cat /config/config.boot")
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
                        publish_data["devices"][mac_address] = {"hostname": hostname, "ip": ip_address, "mac": mac_address}
                    hostname = ip_address = mac_address = None
                elif "ip-address " in line:
                    ip_address = line.strip().split(" ")[1]
                elif "mac-address " in line:
                    mac_address = line.strip().split(" ")[1]

        self.redis_instance.publish("home:broadcast:generic", json.dumps({"key": "dhcp-leases", "content": publish_data}))

    def run(self):
        while True:
            self.poll_dhcp_leases()
            time.sleep(5)

def main():
    setproctitle("dhcp_leases_publisher: run")
    dlp = DhcpLeasesPublisher()
    dlp.run()

if __name__ == '__main__':
    main()
