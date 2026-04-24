from django.urls import path, include
from rest_framework.routers import DefaultRouter

from payment.views import PaymentViewSet, stripe_webhook

router = DefaultRouter()
router.register(r'payment', PaymentViewSet)

urlpatterns = [
    path('payment/webhook/', stripe_webhook, name='stripe-webhook'),
    path('', include(router.urls)),
]