from rest_framework.serializers import ModelSerializer

from app.models import SorteoHora


class SorteoHoraSerializer(ModelSerializer):
    class Meta:
        model = SorteoHora
        fields = ('id', 'hora_sorteo',)