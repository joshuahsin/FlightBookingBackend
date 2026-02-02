from rest_framework import viewsets, status

from user.models import User
from user.permissions import UserPermission
from user.serializers import UserSerializer, RegisterSerializer
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response


# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [UserPermission]

    def get_serializer_class(self):
        if self.action == 'create':
            return RegisterSerializer
        return UserSerializer

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