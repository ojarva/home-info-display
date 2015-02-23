from setproctitle import setproctitle
import json
import redis
import subprocess
import time

class DisplayControlConsumer(object):
    STEP = 0.05

    def __init__(self):
        self.redis_instance = redis.StrictRedis()
        self.env = {"DISPLAY": ":0"}


    def get_brightness(self):
        p = subprocess.Popen(["xrandr", "--verbose"], env=self.env, stdout=subprocess.PIPE)
        (stdout, _) = p.communicate()
        for line in stdout.split("\n"):
            if "Brightness" in line:
                return float(line.strip().split(": ")[1])

    def set_brightness(self, brightness):
        p = subprocess.Popen(["xrandr", "--q1", "--output", "HDMI-0", "--brightness", unicode(brightness)], env=self.env)
        p.wait()
        self.redis_instance.setex("display-control-brightness", 60, brightness)

    def run(self):
        while True:
            time.sleep(1)
            destination_brightness = self.redis_instance.get("display-control-destination-brightness")
            if not destination_brightness:
                continue
            destination_brightness = float(destination_brightness)

            current_brightness = self.redis_instance.get("display-control-brightness")
            if current_brightness:
                current_brightness = float(current_brightness)
            else:
                current_brightness = self.get_brightness()
                self.redis_instance.setex("display-control-brightness", 60, current_brightness)

            if current_brightness > destination_brightness:
                # Decrease brightness. Current brightness is too large.
                new_brightness = current_brightness - self.STEP
                print "Decreasing brightness: %s (-> %s, currently at %s)" % (new_brightness, destination_brightness, current_brightness)
                if new_brightness < destination_brightness:
                    # Wrapped around: new brightness is smaller than destination brightness.; no action
                    print "Brightness wrapped around"
                    self.redis_instance.delete("display-control-destination-brightness")
                    continue
            elif current_brightness < destination_brightness:
                # Increase brightness
                new_brightness = current_brightness + self.STEP
                print "Increasing brightness: %s (-> %s, currently at %s)" % (new_brightness, destination_brightness, current_brightness)

                if new_brightness > destination_brightness:
                    # Wrapped around; no action
                    self.redis_instance.delete("display-control-destination-brightness")
                    continue
            else:
                # Already matches. No action.
                self.redis_instance.delete("display-control-destination-brightness")
                continue
            print "Setting brightness to %s (destination: %s)" % (new_brightness, destination_brightness)
            self.set_brightness(new_brightness)
            self.redis_instance.publish("home:broadcast:generic", json.dumps({"key": "display_brightness", "content": new_brightness}))
def main():
    setproctitle("display_control_consumer: run")
    dcc = DisplayControlConsumer()
    dcc.run()

if __name__ == '__main__':
    main()
