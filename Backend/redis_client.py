import os
import redis.asyncio as redis
from kombu.utils.url import safequote

redis_host = "127.0.0.1"  # safequote(os.environ.get("REDIS_HOST", "localhost"))
# the  above code says use the host from environment by the name REDIS_HOST,
# if nothing of such is available, then use the localhost
redis_client = redis.Redis(host=redis_host, port=6379, db=0)
#


async def add_key_value_redis(key, value, expire=None):
    await redis_client.set(key, value)
    print(key, value)
    if expire:
        await redis_client.expire(key, expire)
    # await add_key_value_redis("testkey", "testvalue", expire=30)
    # value = await get_value_redis("testkey")
    # print("Value fetched:", value)


async def get_value_redis(key):
    return await redis_client.get(key)


async def delete_key_redis(key):
    await redis_client.delete(key)
