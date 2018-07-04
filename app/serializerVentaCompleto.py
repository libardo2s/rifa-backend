from rest_framework.serializers import ModelSerializer

from app.models import Venta
from app.serializerTaquilla import TaquillaSerializer
from app.serializerVentaDetalle import VentaDetalleSerializer


class VentaSerializerCompleto(ModelSerializer):
    list_detalles = VentaDetalleSerializer(many=True)
    taquilla = TaquillaSerializer(many=False)

    class Meta:
        model = Venta
        fields = ('id', 'fecha', 'time', 'serial_cobro', 'total_apostado', 'list_detalles', 'total_ganancia', 'estado', 'taquilla')
