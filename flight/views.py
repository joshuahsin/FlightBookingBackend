from rest_framework import viewsets
from rest_framework.filters import SearchFilter

from user.permissions import IsAdminOrReadOnly
from .models import Flight
from .serializers import FlightSerializer

# Create your views here.
class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter]
    search_fields = [
        "^departure_airport__airport_code",
        "arrival_airport__airport_code",
        "departure_airport__city__name",  # search by departure airport city name
        "arrival_airport__city__name",    # search by arrival airport city name
    ]

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by departure city name
        departure_city = self.request.query_params.get('departure_city')
        if departure_city:
            queryset = queryset.filter(departure_airport__city__name__icontains=departure_city)
        
        # Filter by arrival city name
        arrival_city = self.request.query_params.get('arrival_city')
        if arrival_city:
            queryset = queryset.filter(arrival_airport__city__name__icontains=arrival_city)
        
        return queryset