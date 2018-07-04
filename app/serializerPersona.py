from rest_framework.serializers import ModelSerializer
from app.models import Persona


class PersonaSerializer(ModelSerializer):
    class Meta:
        model = Persona
        fields = ('id', 'documento', 'nombres', 'apellidos', 'correo')

    def create(self, validated_data):
        return Persona.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.documento = validated_data.get('documento', instance.documento)
        instance.nombres = validated_data.get('nombres', instance.nombres)
        instance.apellidos = validated_data.get('apellidos', instance.nombres)
        instance.apellidos = validated_data.get('correo', instance.correo)
        instance.save()
        return instance