from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework import status
from core.models import Usuarios, Roles
from django.contrib.auth.hashers import make_password
import uuid
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    rol = Roles.objects.get(pk=request.data['id_rol'])

    auth_user = User.objects.create_user(
        username=request.data['usuario'],
        email=request.data['correo'],
        password=request.data['contrasena']
    )

    usuario_extra = Usuarios.objects.create(
        id_usuario=uuid.uuid4(),
        user=auth_user,
        nombre=request.data['nombre'],
        apellido=request.data['apellido'],
        correo=request.data['correo'],
        usuario=request.data['usuario'],
        contrasena=make_password(request.data['contrasena']),
        id_rol=rol
    )

    token = Token.objects.create(user=auth_user)

    return Response({
        'token': token.key,
        'user': {
            'id_usuario': usuario_extra.id_usuario,
            'nombre': usuario_extra.nombre,
            'apellido': usuario_extra.apellido,
            'correo': usuario_extra.correo,
            'usuario': usuario_extra.usuario,
            'id_rol': usuario_extra.id_rol.id_rol
        }
    }, status=status.HTTP_201_CREATED)