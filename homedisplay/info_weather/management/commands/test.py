import xmltodict
import pprint
import json

f = open("test.xml").read()

data = xmltodict.parse(f)
data = json.loads(json.dumps(data))

for hour in data["weather"]["hbhf"]["hour"]:
  pprint.pprint(hour)
