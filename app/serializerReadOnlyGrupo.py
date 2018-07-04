from rest_framework.serializers import ModelSerializer
from app.models import Grupo


class GrupoSerializerReadOnly(ModelSerializer):
    class Meta:
        model = Grupo
        fields = ('id', 'nombreGrupo', 'estado', 'countTaquillas', 'propietarios')

    def create(self, validated_data):
        return Grupo.objects.create(**validated_data)