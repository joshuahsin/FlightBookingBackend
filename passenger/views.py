from rest_framework import viewsets

from user.permissions import IsAdmin, IsUser, IsUserOrAdmin
from .models import Passenger
from .serializers import PassengerSerializer


class PassengerViewSet(viewsets.ModelViewSet):
    queryset = Passenger.objects.all()
    serializer_class = PassengerSerializer

    def get_permissions(self):
        if self.action == 'create' or self.action == 'partial_update':
            return [IsUser()]
        if self.action == 'list':
            return [IsUserOrAdmin()]
        return [IsAdmin()]

    def get_queryset(self):
        qs = Passenger.objects.all()
        params = self.request.query_params

        if first_name := params.get('first_name'):
            qs = qs.filter(first_name__icontains=first_name)
        if last_name := params.get('last_name'):
            qs = qs.filter(last_name__icontains=last_name)
        if passport_number := params.get('passport_number'):
            qs = qs.filter(passport_number__iexact=passport_number)
        if date_of_birth := params.get('date_of_birth'):
            qs = qs.filter(date_of_birth=date_of_birth)

        return qs