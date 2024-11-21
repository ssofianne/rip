from django.utils.deprecation import MiddlewareMixin
from django.http import HttpRequest
from reconstruction.models import CustomUser 
from django.conf import settings
import redis

# Подключение к Redis
session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

class RedisSessionMiddleware(MiddlewareMixin):
    def process_request(self, request: HttpRequest):
        session_id = request.COOKIES.get('session_id')
        if session_id:
            user_id = session_storage.get(session_id)
            if user_id:
                try:
                    request.user = CustomUser.objects.get(pk=int(user_id))
                except CustomUser.DoesNotExist:
                    request.user = None
        else:
            request.user = None
