from rest_framework import serializers
from cabin_class.models import CabinClass

class CabinClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = CabinClass
        fields = '__all__'