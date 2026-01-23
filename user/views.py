from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from user.models import User
from user.permissions import IsAdminOrReadOnly
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
    permission_classes = [IsAdminOrReadOnly]

    def is_admin(self):
        return self.request.user.role == "admin"

    def get_queryset(self):
        if self.is_admin() == False:
            return User.objects.get_queryset().filter(id=self.request.user.id)
        return User.objects.all()

    def perform_create(self, serializer):
        if self.request.user.role is not None:
            raise PermissionDenied("Only users without a role can create a user")
        serializer.save()

    def perform_update(self, serializer):
        if self.is_admin():
            raise PermissionDenied("You are not allowed to update this user")

        if serializer.id != self.request.user.id:
            raise PermissionDenied("You are not allowed to update this user")
        serializer.save()

    def perform_destroy(self, instance):
        if self.is_admin():
            raise PermissionDenied("You are not allowed to delete this user")

        if instance.id != self.request.user.id:
            raise PermissionDenied("You are not allowed to delete this user")
        instance.delete()

class UserTokenView(TokenObtainPairView):
    permission_classes = [AllowAny]

class UserTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]