from rest_framework import serializers
from core.models import Equipos

class CreaEquipoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipos
        fields = ['nombre_equipo', 'descripcion']
