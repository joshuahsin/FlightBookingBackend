from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.filters import SearchFilter

from user.permissions import IsAdminOrReadOnly
from .models import Airport
from .serializers import AirportSerializer

# Create your views here.
class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    filter_backends = [SearchFilter]
    search_fields = [
        "^airport_code",      # prefix search (fast, ideal for airport codes)
        "airport_name",       # search by airport name
        "city__name",         # search by city name
    ]
    permission_classes = [IsAdminOrReadOnly]