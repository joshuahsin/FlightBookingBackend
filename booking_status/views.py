from rest_framework import viewsets
#from rest_framework.permissions import IsAdminUser

from booking_status.models import BookingStatus
from booking_status.serializers import BookingStatusSerializer
from user.permissions import IsAdminOrReadOnly


# Create your views here.

class BookingStatusViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BookingStatus.objects.all()
    serializer_class = BookingStatusSerializer
    permission_classes = [IsAdminOrReadOnly]