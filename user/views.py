from rest_framework import viewsets

from user.models import User
from user.permissions import UserPermission
from user.serializers import UserSerializer
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.permissions import AllowAny


# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [UserPermission]

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.role == "admin":
            return User.objects.all()
        if self.request.user.is_authenticated:
            return User.objects.filter(id=self.request.user.id)
        return User.objects.none()


class UserTokenView(TokenObtainPairView):
    permission_classes = [AllowAny]

class UserTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]