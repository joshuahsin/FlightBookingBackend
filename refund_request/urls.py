from django.urls import path, include
from rest_framework.routers import DefaultRouter

from refund_request.views import RefundRequestViewSet

router = DefaultRouter()
router.register(r'refund-request', RefundRequestViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
