from rest_framework import serializers
from api.models import CarnotTable


class CarnotTableSerializers(serializers.ModelSerializer):
    class Meta:
        model = CarnotTable
        fields = "__all__"
