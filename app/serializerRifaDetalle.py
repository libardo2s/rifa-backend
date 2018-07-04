from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from app.models import RifaLista


class RifaListaSerializer(ModelSerializer):

    image = serializers.ImageField(max_length=None, use_url=True)

    class Meta:
        model = RifaLista
        fields = ('id', 'posicion', 'image', 'nombre_imagen', 'rifa')

    def create(self, validated_data):
        return RifaLista.objects.create(**validated_data)