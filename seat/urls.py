from django.urls import path, include
from rest_framework.routers import DefaultRouter

from seat.views import SeatViewSet

router = DefaultRouter()
router.register('seat', SeatViewSet)

urlpatterns = [
    path('', include(router.urls))
]