from rest_framework import routers
from django.urls import include, path
from fare.views import FareViewSet

router = routers.DefaultRouter()
router.register(r'fare', FareViewSet)

urlpatterns = [
    path('', include(router.urls)),
]