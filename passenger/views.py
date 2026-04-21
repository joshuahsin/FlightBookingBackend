from django.shortcuts import render
from rest_framework import viewsets

from user.permissions import IsAdmin, IsUserOrAdmin
from .models import Passenger
from .serializers import PassengerSerializer


# Create your views here.

class PassengerViewSet(viewsets.ModelViewSet):
    queryset = Passenger.objects.all()
    serializer_class = PassengerSerializer

    def get_permissions(self):
        # Checkout: any logged-in user may POST; other actions stay admin-only.
        if self.action == 'create':
            return [IsUserOrAdmin()]
        return [IsAdmin()]