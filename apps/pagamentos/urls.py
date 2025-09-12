from django.urls import path
from .views import payments_views as payment_views
from .webhooks import mercadopago_webhook

app_name = 'pagamentos'

urlpatterns = [
    path('create/', payment_views.CreatePaymentView.as_view(), name='create_payment'),
    path('success/', payment_views.PaymentSuccessView.as_view(), name='payment_success'),
    path('failure/', payment_views.PaymentFailureView.as_view(), name='payment_failure'),
    path('pending/', payment_views.PaymentPendingView.as_view(), name='payment_pending'),
    path('webhook/mercadopago/', mercadopago_webhook.MercadoPagoWebhookView.as_view(), name='webhook_mercadopago'),
    path('history/', payment_views.PaymentHistoryView.as_view(), name='payment_history'),
]