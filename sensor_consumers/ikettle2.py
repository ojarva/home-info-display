commands = {
    "autoDacKettle": 44,
    "autoDacKettleResponse": 45,
    "endMessage": 126,
    "kettleScheduleRequest": 65,
    "kettleStatus": 20,
    "turnOffKettle": 22,
    "turnOnKettle": 21,
    "configureWifi": 12,
    "configureWifiSSID": 5,
    "configureWifiPassword": 7,
    "listWifiNetworks": 13,
    "deviceInfo": 100,
    "firmwareUpdate": 109,
    "commandSentAck": 3,
    "kettleOffBase": 7,
    "kettleOnBase": 8,
    "wifiNetworkResponse": 14,
    "deviceInfoResponse": 101,
    "deviceKettle": 1,
    "deviceCoffee": 2,
}

import socket
import pickle
import sys
import select
import time

def get_status(value):
    if value == 0:
        return "ready"
    if value == 1:
        return "boiling"
    if value == 2:
        return "keep-warm"
    if value == 3:
        return "finished"
    if value == 4:
        return "cooling"



def read_all_available(proc):
    ret = ""
    while select.select([proc.stdout], [], [], 0)[0] != []:
        ret += proc.stdout.read(1)
    return ret


class Kettle2:

    def __init__(self, ip, port=2081):
        self.TCP_IP = ip
        self.TCP_PORT = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.s.connect((self.TCP_IP, self.TCP_PORT))

    def disconnect(self):
        self.s.close()

    def on(self, temperature=100):
        converted_temperature = hex(temperature).replace("0x", "")
        message = ("15%s007e" % converted_temperature).decode("hex")
        self.s.send(message)

    def off(self):
        message = "167e".decode("hex")
        self.s.send(message)

    def read(self):
        data = ""
        while select.select([self.s], [], [], 0.1)[0] != []:
            inp = self.s.recv(1024)
            if inp is None:
                break
            data += inp
        return self.parse(data)

    def parse(self, data):
        message_open = False
        message_data = ""
        output = []
        for ch in data:
            item = ch.encode("hex")
            message_data += ch
            if item == "7e":
                buf = []
                for collected_ch in message_data:
                    item = collected_ch.encode("hex")
                    int_value = int(item, 16)
                    buf.append(int_value)
                if buf[0] == 20:
                    if len(buf) != 7:
                        continue
                    parsed = {}
                    parsed["status"] = get_status(buf[1])
                    parsed["temperature"] = buf[2]
                    parsed["present"] = True
                    if parsed["temperature"] > 110:
                        parsed["present"] = False
                    water_level1 = buf[3]
                    water_level2 = buf[4]
                    water_level = (water_level1 << 8) + water_level2
                    parsed["water_level_raw"] = water_level
                    water_level = water_level - 2095
                    if water_level < 0:
                        water_level_parsed = "empty"
                    elif water_level < 30: # < 1/3
                        water_level_parsed = "too_low"
                    elif water_level < 95: # < 2/3
                        water_level_parsed = "half"
                    elif water_level < 150:
                        water_level_parsed = "full"
                    else:
                        water_level_parsed = "overfill"
                    parsed["water_level"] = water_level_parsed

                    output.append({"type": "status", "data": parsed})
                if buf[0] == 3:
                    output.append({"type": "ack"})

                message_open = False
                message_data = ""
        return output

def main(ip):
    kettle = Kettle2(ip)
    kettle.connect()
    for _ in range(1, 10000):
        data = kettle.read()
        if len(data) > 0:
            print data
        time.sleep(0.1)
    kettle.disconnect()


if __name__ == '__main__':
    main(sys.argv[1])
