from django.middleware.csrf import CsrfViewMiddleware
from django.http import HttpResponse
from .views import session_storage
from .models import CustomUser


def session_middleware(get_response):
    def middleware(request):

        csrf_middleware = CsrfViewMiddleware(get_response)

        ssid = request.COOKIES.get("session_id")
        if ssid and session_storage.exists(ssid):
            email = session_storage.get(ssid).decode("utf-8")
            request.user = CustomUser.objects.get(email=email)
        else:
            request.user = None

        response = csrf_middleware.process_view(request, None, (), {})

        if response is None:  # Если CSRF проверка прошла, продолжаем обработку запроса
            response = get_response(request)

        return response

    return middleware