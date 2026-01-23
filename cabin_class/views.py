from django.shortcuts import render
from rest_framework import viewsets
#from rest_framework.permissions import IsAdminUser

from cabin_class.serializers import CabinClassSerializer
from cabin_class.models import CabinClass
from user.permissions import IsAdminOrReadOnly


# Create your views here.
class CabinClassViewSet(viewsets.ModelViewSet):
    queryset = CabinClass.objects.all()
    serializer_class = CabinClassSerializer
    permission_classes = [IsAdminOrReadOnly]