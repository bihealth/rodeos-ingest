from pytest_redis import factories

#: Define ``redisdb`` fixture to connect to an already running redis server
#: such as on CI.
redisdb = factories.redisdb("redis_nooproc")
