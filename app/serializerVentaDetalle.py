from rest_framework.serializers import ModelSerializer
from app.models import VentaDetalle
from app.serializerRifaDetalle import RifaListaSerializer
from app.sorteoSerializer import SorteoSerializer


class VentaDetalleSerializer(ModelSerializer):
    # detalle_rifa = RifaListaSerializer(many=False)
    sorteo = SorteoSerializer(many=False)

    class Meta:
        model = VentaDetalle
        fields = ('id', 'numeros', 'sorteo', 'valor_apuesta', 'ganancia', 'estado')
        # fields = ('id', 'detalle_rifa', 'sorteo', 'valor_apuesta', 'estado')
