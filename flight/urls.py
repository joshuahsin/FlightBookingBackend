from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import FlightViewSet

router = DefaultRouter()
router.register(r'flight', FlightViewSet)

urlpatterns = [
    path('', include(router.urls)),
]