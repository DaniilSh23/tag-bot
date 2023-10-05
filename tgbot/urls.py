from django.urls import path
from django.conf.urls.static import static
from tag_bot import settings


app_name = 'tgbot'

urlpatterns = []

# Определяем путь к статике и медиа, когда дебаг включен
if settings.DEBUG:
    urlpatterns.extend(
        static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    )

    urlpatterns.extend(
        static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    )
