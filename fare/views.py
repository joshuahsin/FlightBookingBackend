from django.core.cache import cache
from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from fare.models import Fare
from fare.serializers import FareSerializer
from user.permissions import IsAdminOrReadOnly

# --- Cache config (list by flight_id) ---
FARE_LIST_CACHE_TIMEOUT = 300

def _fare_list_cache_key(flight_id):
    return f"flightbooking:fare_list:flight_{flight_id}"


def _list_request_is_cacheable(request):
    """Only cache when request has flight_id and no other filters."""
    q = request.query_params
    return (
        q.get("flight_id")
        and not q.get("cabin_class")
        and not q.get("search", "").strip()
    )


class FareViewSet(viewsets.ModelViewSet):
    queryset = Fare.objects.all()
    serializer_class = FareSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter]
    search_fields = ["cabin_class__cabin_class_name", "flight__id"]

    # --- Queryset ---
    def get_queryset(self):
        qs = super().get_queryset().select_related("flight", "cabin_class")
        params = self.request.query_params
        if flight_id := params.get("flight_id"):
            qs = qs.filter(flight_id=flight_id)
        if cabin := params.get("cabin_class"):
            qs = qs.filter(cabin_class__cabin_class_name__iexact=cabin)
        return qs

    # --- List (with cache when ?flight_id= only) ---
    def list(self, request, *args, **kwargs):
        if not _list_request_is_cacheable(request):
            return super().list(request, *args, **kwargs)

        flight_id = request.query_params.get("flight_id")
        cache_key = _fare_list_cache_key(flight_id)
        cached = cache.get(cache_key)
        if cached is not None:
            r = Response(cached)
            r["X-Cache"] = "HIT"
            return r

        r = super().list(request, *args, **kwargs)
        if r.status_code == 200:
            cache.set(cache_key, r.data, FARE_LIST_CACHE_TIMEOUT)
        r["X-Cache"] = "MISS"
        return r

    # --- Cache invalidation ---
    def _invalidate_fare_cache_for_flight(self, flight_id):
        cache.delete(_fare_list_cache_key(flight_id))

    # --- Write actions (invalidate cache) ---
    def perform_create(self, serializer):
        instance = serializer.save()
        self._invalidate_fare_cache_for_flight(instance.flight_id)

    def perform_update(self, serializer):
        instance = serializer.save()
        self._invalidate_fare_cache_for_flight(instance.flight_id)

    def perform_destroy(self, instance):
        flight_id = instance.flight_id
        instance.delete()
        self._invalidate_fare_cache_for_flight(flight_id)