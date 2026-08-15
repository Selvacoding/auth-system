import time
from fastapi import Request, HTTPException, status
import redis

import CONFIG

redis_client = redis.Redis(host=CONFIG.REDIS_HOST, port=CONFIG.REDIS_PORT, decode_responses=True)

class RateLimiter:
    def __init__(self, times: int, seconds: int, prefix: str = "rate_limit"):
        self.times = times
        self.seconds = seconds
        self.prefix = prefix

    def _get_client_ip(self, request: Request) -> str:
        # forwarded = request.headers.get("x-forwarded-for")
        # if forwarded:
        #     return forwarded.split(",")[0].strip()
        return request.client.host

    def __call__(self, request: Request):
        client_ip = self._get_client_ip(request)
        key = f"{self.prefix}:{client_ip}"
        current = redis_client.incr(key)

        if current == 1:
            redis_client.expire(key, self.seconds)

        if current > self.times:
            ttl = redis_client.ttl(key)
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                                detail=f"Too many attempts. Try again in {ttl} seconds.",
                            )
        return current