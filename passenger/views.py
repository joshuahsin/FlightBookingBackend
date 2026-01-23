from django.shortcuts import render
from rest_framework import viewsets

from user.permissions import IsAdmin
from .models import Passenger
from .serializers import PassengerSerializer


# Create your views here.

class PassengerViewSet(viewsets.ModelViewSet):
    queryset = Passenger.objects.all()
    serializer_class = PassengerSerializer
    permission_classes = [IsAdmin]