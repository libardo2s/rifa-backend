from rest_framework.serializers import ModelSerializer

from app.models import EstadoSistema


class EstadoSistemaSerializer(ModelSerializer):
    class Meta:
        model = EstadoSistema
        fields = ('id', 'nombre', 'estado')

    def create(self, validated_data):
        return EstadoSistema.objects.create(**validated_data)
