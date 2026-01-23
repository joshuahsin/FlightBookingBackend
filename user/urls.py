from django.urls import path, include
from rest_framework.routers import DefaultRouter

from user.views import UserViewSet, UserTokenView, UserTokenRefreshView

router = DefaultRouter()
router.register('user', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path("token/", UserTokenView.as_view(), name="token"),
    path("token/refresh/", UserTokenRefreshView.as_view(), name="token_refresh"),
]