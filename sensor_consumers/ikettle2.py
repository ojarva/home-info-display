"""
2075 +-5 = empty
2153 +-5 = 6dl
2210 +-5 = 12dl
2260 +-5 = 18dl
"""

import socket
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


class Kettle2(object):

    def __init__(self, ip, port=2081):
        self.tcp_ip = ip
        self.tcp_port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.s.connect((self.tcp_ip, self.tcp_port))

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
        message_data = ""
        output = []
        for input_byte in data:
            item = input_byte.encode("hex")
            message_data += input_byte
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
                    water_level = water_level - 2075
                    water_level_percentage = round(
                        min(1, max(0, float(water_level) / 185)), 3)
                    if not parsed["present"]:
                        water_level_percentage = None
                    parsed["water_level"] = water_level_percentage

                    output.append({"type": "status", "data": parsed})
                if buf[0] == 3:
                    output.append({"type": "ack"})

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
