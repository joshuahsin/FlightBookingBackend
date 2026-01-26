from django.urls import path, include
from rest_framework.routers import DefaultRouter
from city.views import CityViewSet

router = DefaultRouter()
router.register(r'city', CityViewSet)

urlpatterns = [
    path('', include(router.urls)),
]