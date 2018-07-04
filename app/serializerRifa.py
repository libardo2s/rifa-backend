from rest_framework.serializers import ModelSerializer
from app.models import Rifa
from app.serializerRifaDetalle import RifaListaSerializer


class RifaSerializer(ModelSerializer):
    #lista_elements = RifaListaSerializer(many=True)
    class Meta:
        model = Rifa
        fields = ('id', 'nombre_rifa', 'elementos')

    def create(self, validated_data):
        return Rifa.objects.create(**validated_data)