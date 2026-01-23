from django.shortcuts import render
from rest_framework import viewsets

from fare.models import Fare
from fare.serializers import FareSerializer
from user.permissions import IsAdminOrReadOnly


# Create your views here.

class FareViewSet(viewsets.ModelViewSet):
    queryset = Fare.objects.all()
    serializer_class = FareSerializer
    permission_classes = [IsAdminOrReadOnly]