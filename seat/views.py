from rest_framework import viewsets

from seat.models import Seat
from seat.serializers import SeatSerializer
from user.permissions import IsAdminOrReadOnly


# Create your views here.

class SeatViewSet(viewsets.ModelViewSet):
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer
    permission_classes = [IsAdminOrReadOnly]