import redis

r = redis.Redis(host="127.0.0.1", port=6379)  # (host="172.22.171.83", port=6379)
r.set("foo", "bar")
print(r.ping())
print(r.get("foo"))
