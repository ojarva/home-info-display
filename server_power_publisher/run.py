import manage_server_power
import time
import subprocess
import local_settings
import redis

redis_instance = redis.StrictRedis()

sp = manage_server_power.ServerPower(server_hostname=local_settings.SERVER_IP_ADDRESS, server_mac=local_settings.SERVER_MAC_ADDRESS, ssh_username=local_settings.SERVER_SSH_USERNAME, broadcast_ip=local_settings.SERVER_BROADCAST_IP)


def check_server_power():
    status = "unknown"
    alive_status = sp.is_alive()
    if alive_status == manage_server_power.SERVER_UP:
        status = "running"
    elif alive_status == manage_server_power.SERVER_UP_NOT_RESPONDING:
        status = "not_responding"
    elif alive_status == manage_server_power.SERVER_DOWN:
        status = "down"
    redis_instance.publish("home:broadcast:server_power", status)

if __name__ == '__main__':
    while True:
        check_server_power()
        time.sleep(1)
