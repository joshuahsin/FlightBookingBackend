from django.urls import path, include
from rest_framework.routers import DefaultRouter

from booking_status.views import BookingStatusViewSet

router = DefaultRouter()
router.register(r'booking-status', BookingStatusViewSet)

urlpatterns = [
    path('', include(router.urls))
]