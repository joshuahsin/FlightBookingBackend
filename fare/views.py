from rest_framework import viewsets
from rest_framework.filters import SearchFilter

from fare.models import Fare
from fare.serializers import FareSerializer
from user.permissions import IsAdminOrReadOnly


# Create your views here.

class FareViewSet(viewsets.ModelViewSet):
    queryset = Fare.objects.all()
    serializer_class = FareSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter]
    search_fields = [
        "cabin_class__cabin_class_name",  # search by cabin class name
        "flight__id",                      # search by flight id
    ]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by flight id
        flight_id = self.request.query_params.get("flight_id")
        if flight_id:
            queryset = queryset.filter(flight_id=flight_id)

        # Filter by cabin class name
        cabin_class_name = self.request.query_params.get("cabin_class")
        if cabin_class_name:
            queryset = queryset.filter(
                cabin_class__cabin_class_name__iexact=cabin_class_name
            )

        return queryset