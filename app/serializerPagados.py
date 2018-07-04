from rest_framework.serializers import ModelSerializer

from app.models import Venta
from app.serializerTaquilla import TaquillaSerializer
from app.serializerUser import UserSerializer


class PagadoSerializer(ModelSerializer):
    taquilla = TaquillaSerializer(many=False)
    usuarioPagador = UserSerializer(many=False)

    class Meta:
        model = Venta
        fields = ('id', 'fecha', 'time', 'total_apostado', 'total_ganancia', 'estado', 'taquilla', 'fecha_pago', 'usuarioPagador')
