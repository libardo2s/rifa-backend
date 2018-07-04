from rest_framework.serializers import ModelSerializer

from app.models import Venta


class VentaSerializerTaquilla(ModelSerializer):
    class Meta:
        model = Venta
        fields = ('id', 'fecha', 'time', 'total_apostado', 'total_ganancia', 'fecha_pago')
