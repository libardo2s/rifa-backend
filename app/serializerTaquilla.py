from rest_framework.serializers import ModelSerializer
from app.models import Taquilla
from app.serializerReadOnlyGrupo import GrupoSerializerReadOnly
from app.serializerUser import UserSerializer


class TaquillaSerializer(ModelSerializer):
    usuario = UserSerializer(many=False)
    grupo = GrupoSerializerReadOnly(many=False)

    class Meta:
        model = Taquilla
        fields = ('id', 'usuario', 'grupo')

    def create(self, validated_data):
        return Taquilla.objects.create(**validated_data)