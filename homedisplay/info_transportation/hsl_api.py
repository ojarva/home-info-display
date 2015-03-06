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
        # For departures during next day, h>23
        extra_time = datetime.timedelta(0)
        time = ("0%s" % departure_information["time"])[-4:]
        hour = int(time[0:2])
        minute = int(time[2:])
        if hour > 23:
            extra_time = datetime.timedelta(days=1)
            hour -= 24

        timestamp = datetime.datetime.strptime("%s" % departure_information["date"], "%Y%m%d") + extra_time
        timestamp = timestamp.replace(hour=hour).replace(minute=minute)
        return timestamp

    def get_lines(self, stop_number):
        r = requests.get("%s?user=%s&pass=%s&request=stop&code=%s&p=00000010000" % (self.base_url, self.username, self.password, stop_number))
        data = r.json()
        lines = []
        if "lines" not in data[0] or data[0]["lines"] is None:
            return lines
        for line in data[0]["lines"]:
            lines.append(line.strip())
        return lines

    def get_timetable(self, stop_number):
        r = requests.get("%s?user=%s&pass=%s&request=stop&code=%s&p=00000000001&dep_limit=20" % (self.base_url, self.username, self.password, stop_number))
        data = r.json()
        departures = []
        if "departures" not in data[0] or data[0]["departures"] is None:
            return departures
        for departure in data[0]["departures"]:
            timestamp = self.parse_timestamp(departure)
            departures.append({"timestamp": timestamp, "line_number": departure.get("code")})
        return departures
