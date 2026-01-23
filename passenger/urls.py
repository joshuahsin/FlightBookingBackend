from django.urls import path, include
from rest_framework.routers import DefaultRouter

from passenger.views import PassengerViewSet

router = DefaultRouter()
router.register(r'passenger', PassengerViewSet)

urlpatterns = [
    path('', include(router.urls))
]