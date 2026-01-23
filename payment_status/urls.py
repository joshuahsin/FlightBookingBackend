from rest_framework.routers import DefaultRouter
from django.urls import path, include

from payment_status.views import PaymentStatusViewSet

router = DefaultRouter()
router.register(r'payment-status', PaymentStatusViewSet)

urlpatterns = [
    path('', include(router.urls)),
]