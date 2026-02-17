from django.core.cache import cache
from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from user.permissions import IsAdminOrReadOnly
from .models import Airport
from .serializers import AirportSerializer

# Cache key and TTL for airport list (Redis or LocMem when REDIS_URL unset)
AIRPORT_LIST_CACHE_KEY = "flightbooking:airport_list"
AIRPORT_LIST_CACHE_TIMEOUT = 300  # seconds

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

    def get_queryset(self):
        return super().get_queryset().select_related("city")

    def _invalidate_airport_list_cache(self):
        cache.delete(AIRPORT_LIST_CACHE_KEY)

    def list(self, request, *args, **kwargs):
        # Only cache the full list; skip cache when ?search= is used
        if request.query_params.get("search", "").strip():
            return super().list(request, *args, **kwargs)

        cached = cache.get(AIRPORT_LIST_CACHE_KEY)
        if cached is not None:
            response = Response(cached)
            response["X-Cache"] = "HIT"
            return response

        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        cache.set(AIRPORT_LIST_CACHE_KEY, data, AIRPORT_LIST_CACHE_TIMEOUT)
        response = Response(data)
        response["X-Cache"] = "MISS"
        return response

    def perform_create(self, serializer):
        super().perform_create(serializer)
        self._invalidate_airport_list_cache()

    def perform_update(self, serializer):
        super().perform_update(serializer)
        self._invalidate_airport_list_cache()

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        self._invalidate_airport_list_cache()