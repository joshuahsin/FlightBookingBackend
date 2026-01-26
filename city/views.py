from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from city.models import City
from city.serializers import CitySerializer
from user.permissions import IsAdminOrReadOnly

# Create your views here.
class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter]
    search_field = ["^name"]