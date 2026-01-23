from django.urls import path, include
from rest_framework.routers import DefaultRouter

from order_status.views import OrderStatusView

router = DefaultRouter()
router.register(r'order-status', OrderStatusView)

urlpatterns = [
    path('', include(router.urls))
]