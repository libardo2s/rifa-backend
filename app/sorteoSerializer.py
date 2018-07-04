from rest_framework.serializers import ModelSerializer

from app.models import Sorteo
from app.serializerRifa import RifaSerializer
from app.sorteoHoraSerializer import SorteoHoraSerializer


class SorteoSerializer(ModelSerializer):
    rifa = RifaSerializer(many=False)
    sorteoHoras = SorteoHoraSerializer(many=False)
    class Meta:
        model = Sorteo
        fields = ('id', 'rifa', 'sorteoHoras', 'fecha_sorteo', 'numero_ganador')
