from rest_framework.serializers import ModelSerializer
from app.models import Grupo
from app.serializerAdministrador import AdministradorSerializer
from app.serializerTaquilla import TaquillaSerializer


class GrupoSerializer(ModelSerializer):
    taquillas = TaquillaSerializer(many=True)
    administrador = AdministradorSerializer(many=False)

    class Meta:
        model = Grupo
        fields = ('id', 'nombreGrupo', 'estado', 'countTaquillas', 'taquillas', 'administrador', 'propietarios')

    def create(self, validated_data):
        return Grupo.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.nombreGrupo = validated_data.get('nombreGrupo', instance.nombreGrupo)
        instance.save()
        return instance