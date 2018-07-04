from rest_framework.serializers import ModelSerializer

from app.models import Permisos


class PermisoSerializer(ModelSerializer):
    class Meta:
        model = Permisos
        fields = ('id', 'permiso_name', 'permiso_uri')
