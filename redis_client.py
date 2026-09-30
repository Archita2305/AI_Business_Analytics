import redis

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)


#def test_redis():
    #redis_client.set("test", "Redis is working")
    #return redis_client.get("test")