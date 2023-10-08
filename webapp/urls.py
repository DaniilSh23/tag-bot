from django.urls import path
from django.conf.urls.static import static
from tag_bot import settings
from webapp.views import BalanceView, sec_pay_step, CheckPayment

app_name = 'webapp'

urlpatterns = [
    path('balance/', BalanceView.as_view(), name='balance'),
    path('sec_pay_step/', sec_pay_step, name='sec_pay_step'),
    path('check_payment/', CheckPayment.as_view(), name='check_payment'),
]

# Определяем путь к статике и медиа, когда дебаг включен
if settings.DEBUG:
    urlpatterns.extend(
        static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    )

    urlpatterns.extend(
        static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)
    )

