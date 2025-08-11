from rest_framework import serializers
from django.contrib.auth.models import User
from core.models import Usuarios

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Usuarios
        fields = ['nombre', 'apellido', 'correo', 'contrasena', 'usuario', 'id_rol']
