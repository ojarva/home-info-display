import datetime
import requests

class HSLApi(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.base_url = "http://api.reittiopas.fi/hsl/prod/"

    @classmethod
    def parse_line_number(cls, description):
        # Line specification and destination are separated by :
        description = description.split(":")[0]
        # First character is area code
        # Last two characters are line variation and direction
        description = description[1:-2]
        # Remove leading zeros
        while description[0] == "0":
            description = description[1:]
        return description.strip()

    @classmethod
    def parse_line_number_raw(cls, description):
        description = description.split(":")[0]
        return description.strip()

    @classmethod
    def parse_destination(cls, description):
        description = description.split(":")[1]
        return description.strip()

    @classmethod
    def parse_timestamp(cls, departure_information):
        return datetime.datetime.strptime("%s %s" % (departure_information["date"], ("0%s" % departure_information["time"])[-4:]), "%Y%m%d %H%M")

    def get_lines(self, stop_number):
        r = requests.get("%s?user=%s&pass=%s&request=stop&code=%s&p=00000010000" % (self.base_url, self.username, self.password, stop_number))
        data = r.json()
        lines = []
        for line in data[0]["lines"]:
            lines.append(line.strip())
        return lines

    def get_timetable(self, stop_number):
        r = requests.get("%s?user=%s&pass=%s&request=stop&code=%s&p=00000000001" % (self.base_url, self.username, self.password, stop_number))
        data = r.json()
        departures = []
        for departure in data[0]["departures"]:
            timestamp = self.parse_timestamp(departure)
            departures.append({"timestamp": timestamp, "line_number": departure.get("code")})
            pass
        return departures
