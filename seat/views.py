from django.core.cache import cache
from rest_framework import viewsets
from rest_framework.response import Response

from seat.models import Seat
from seat.serializers import SeatSerializer
from user.permissions import IsAdminOrReadOnly


SEAT_LIST_CACHE_TIMEOUT = 300
SEAT_LIST_FILTER_PARAMS = ["flight_id", "cabin_class"]

def _seat_list_cache_key(flight_id, cabin_class):
    return f"flightbooking:seat_list:flight_{flight_id}:cabin_class_{cabin_class}"

def _list_request_is_cacheable(request):
    return all(request.query_params.get(p) for p in SEAT_LIST_FILTER_PARAMS)

class SeatViewSet(viewsets.ModelViewSet):
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer
    permission_classes = [IsAdminOrReadOnly]

    def _invalidate_seat_list_cache(self, flight_id, cabin_class):
        cache.delete(_seat_list_cache_key(flight_id, cabin_class))

    def get_queryset(self):
        qs = super().get_queryset().select_related("flight__departure_airport__city", "flight__arrival_airport__city", "cabin_class")
        if flight_id := self.request.query_params.get("flight_id"):
            qs = qs.filter(flight__id=flight_id)
        if cabin_class := self.request.query_params.get("cabin_class"):
            qs = qs.filter(cabin_class__cabin_class_name__iexact=cabin_class)
        
        return qs
    
    def list(self, request, *args, **kwargs):
        if not _list_request_is_cacheable(request):
            return super().list(request, *args, **kwargs)
        
        print(request.query_params)

        flight_id = request.query_params.get("flight_id")
        cabin_class = request.query_params.get("cabin_class")
        cache_key = _seat_list_cache_key(flight_id, cabin_class)
        cached = cache.get(cache_key)
        if cached is not None:
            response = Response(cached)
            response["X-Cache"] = "HIT"
            return response
        
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        cache.set(cache_key, data, SEAT_LIST_CACHE_TIMEOUT)
        response = Response(data)
        response["X-Cache"] = "MISS"
        return response

    def perform_create(self, serializer):
        instance = serializer.save()
        self._invalidate_seat_list_cache(instance.flight_id, instance.cabin_class_id)

    def perform_update(self, serializer):
        instance = serializer.save()
        self._invalidate_seat_list_cache(instance.flight_id, instance.cabin_class_id)

    def perform_destroy(self, instance):
        flight_id = instance.flight_id
        cabin_class_id = instance.cabin_class_id
        instance.delete()
        self._invalidate_seat_list_cache(flight_id, cabin_class_id)