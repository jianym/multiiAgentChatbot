import redis

# 创建连接池，并设置超时重试
pool = redis.ConnectionPool(host='localhost', port=6379, db=0, retry_on_timeout=True)

# 使用连接池创建 Redis 客户端
r = redis.Redis(connection_pool=pool)