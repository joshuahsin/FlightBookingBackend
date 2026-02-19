from django.core.cache import cache
from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from user.permissions import IsAdminOrReadOnly
from .models import Flight
from .serializers import FlightSerializer

FLIGHT_LIST_CACHE_TIMEOUT = 300
FLIGHT_LIST_FILTER_PARAMS = ("departure_city", "arrival_city")

def _flight_list_cache_key(departure_city, arrival_city):
    return f"flightbooking:flight_list:departure_city_{departure_city}:arrival_city_{arrival_city}"

def _list_request_is_cacheable(request):
    return all(request.query_params.get(p) for p in FLIGHT_LIST_FILTER_PARAMS)

# Create your views here.
class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter]
    search_fields = [
        #"^departure_airport__airport_code",
        #"^arrival_airport__airport_code",
        "departure_airport__city__name",  # search by departure airport city name
        "arrival_airport__city__name",    # search by arrival airport city name
    ]

    def get_queryset(self):
        queryset = super().get_queryset().select_related("departure_airport__city", "arrival_airport__city")

        # Filter by departure city name
        departure_city = self.request.query_params.get('departure_city')
        if departure_city:
            queryset = queryset.filter(departure_airport__city__name__icontains=departure_city)
        
        # Filter by arrival city name
        arrival_city = self.request.query_params.get('arrival_city')
        if arrival_city:
            queryset = queryset.filter(arrival_airport__city__name__icontains=arrival_city)
        
        return queryset

    def list(self, request, *args, **kwargs):
        if not _list_request_is_cacheable(request):
            return super().list(request, *args, **kwargs)

        departure_city = request.query_params.get('departure_city')
        arrival_city = request.query_params.get('arrival_city')
        cache_key = _flight_list_cache_key(departure_city.lower(), arrival_city.lower())
        cached = cache.get(cache_key)
        if cached is not None:
            response = Response(cached)
            response["X-Cache"] = "HIT"
            return response
        
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        cache.set(cache_key, data, FLIGHT_LIST_CACHE_TIMEOUT)
        response = Response(data)
        response["X-Cache"] = "MISS"
        return response

    def _invalidate_flight_list_cache(self, departure_city, arrival_city):
        cache.delete(_flight_list_cache_key(departure_city.lower(), arrival_city.lower()))

    def perform_create(self, serializer):
        super().perform_create(serializer)
        self._invalidate_flight_list_cache(serializer.instance.departure_airport.city.name, serializer.instance.arrival_airport.city.name)

    def perform_update(self, serializer):
        super().perform_update(serializer)
        self._invalidate_flight_list_cache(serializer.instance.departure_airport.city.name, serializer.instance.arrival_airport.city.name)

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        self._invalidate_flight_list_cache(instance.departure_airport.city.name, instance.arrival_airport.city.name)