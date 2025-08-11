from rest_framework import serializers
from django.contrib.auth.models import User
from core.models import Usuarios

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Usuarios
        fields = ['contrasena', 'usuario']
