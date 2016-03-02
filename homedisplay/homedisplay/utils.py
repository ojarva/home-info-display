import redis
import json

redis_instance = redis.StrictRedis()


def publish_ws(key, content):
    redis_instance.publish("home:broadcast:generic",
                           json.dumps({"key": key, "content": content}))
