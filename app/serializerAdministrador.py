from rest_framework.serializers import ModelSerializer
from app.models import Administrador
from app.serializerPersona import PersonaSerializer
from app.serializerUser import UserSerializer


class AdministradorSerializer(ModelSerializer):
    persona = PersonaSerializer(many=False)
    usuario = UserSerializer(many=False)

    class Meta:
        model = Administrador
        fields = ('id', 'persona', 'usuarios')

        def create(self, validated_data):
            return Administrador.objects.create(**validated_data)
