from rest_framework import viewsets

from user.permissions import IsAdminOrReadOnly
from .models import Flight
from .serializers import FlightSerializer

# Create your views here.
class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    permission_classes = [IsAdminOrReadOnly]