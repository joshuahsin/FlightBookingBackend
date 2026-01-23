from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CabinClassViewSet

router = DefaultRouter()
router.register(r'cabin-class', CabinClassViewSet)

urlpatterns = [
    path('', include(router.urls)),
]