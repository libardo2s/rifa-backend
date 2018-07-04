from rest_framework.serializers import ModelSerializer

from app.models import Permisos
from app.permisoSerializer import PermisoSerializer
from app.serializerUser import UserSerializer


class PermisoUsuarioSerializer(ModelSerializer):
    usuario = UserSerializer(many=False)
    permiso = PermisoSerializer(many=False)

    class Meta:
        model = Permisos
        fields = ('id', 'permiso', 'usuario')
