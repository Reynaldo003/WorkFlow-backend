from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from login.serializers import UserSerializer
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework import status
from core.models import Usuarios, Roles
from django.contrib.auth.hashers import make_password, check_password
import uuid
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    user = get_object_or_404(User, username=request.data['usuario'])

    if not user.check_password(request.data['contrasena']):
        return Response({"Error": "Contrasena Invalida"}, status=status.HTTP_400_BAD_REQUEST)

    token, created = Token.objects.get_or_create(user=user)
    usuario_extra = get_object_or_404(Usuarios, user=user)

    serializer = UserSerializer(instance=usuario_extra)
    
    return Response({
        "token": token.key,
        "user": serializer.data
        }, status=status.HTTP_200_OK)

@api_view(['POST'])
def profile(request):
    return Response({})

@api_view(['GET', 'PATCH'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def profile(request):
    try:
        usuario_extra = Usuarios.objects.select_related('id_rol').get(user=request.user)
    except Usuarios.DoesNotExist:
        return Response({"detail": "Perfil no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    def serialize(u: Usuarios):
        return {
            "id_usuario": str(u.id_usuario),
            "nombre": u.nombre,
            "apellido": u.apellido,
            "correo": u.correo,
            "contrasena": u.contrasena,
            "usuario": u.usuario,
            "id_rol": getattr(u.id_rol, "id_rol", None),
            "rol_nombre": getattr(u.id_rol, "nombre", None),
            "is_superuser": request.user.is_superuser,
        }

    if request.method == 'GET':
        return Response(serialize(usuario_extra), status=status.HTTP_200_OK)

    # PATCH
    data = request.data
    changed = False

    if "nombre" in data:
        usuario_extra.nombre = data["nombre"]; changed = True
    if "apellido" in data:
        usuario_extra.apellido = data["apellido"]; changed = True
    if "correo" in data:
        usuario_extra.correo = data["correo"]; changed = True
        request.user.email = data["correo"]
        request.user.save(update_fields=["email"])
    if "usuario" in data:
        usuario_extra.usuario = data["usuario"]; changed = True
        request.user.username = data["usuario"]
        request.user.save(update_fields=["username"])

    pwd = data.get("contrasena")
    if pwd:
        try:
            validate_password(pwd, user=request.user)
        except ValidationError as e:
            return Response({"contrasena": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        request.user.set_password(pwd)
        request.user.save()

        if hasattr(usuario_extra, "contrasena"):
            usuario_extra.contrasena = None
        changed = True

        Token.objects.filter(user=request.user).delete()
        new_token = Token.objects.create(user=request.user)

        nuevo_token = new_token.key
    else:
        nuevo_token = None

    es_admin = request.user.is_superuser or (getattr(usuario_extra.id_rol, "nombre", "") or "").lower() == "administrador"

    if "id_rol" in data:
        if not es_admin:
            return Response({"detail": "No tienes permiso para cambiar el rol."}, status=status.HTTP_403_FORBIDDEN)
        try:
            nuevo_rol = Roles.objects.get(pk=data["id_rol"])
            usuario_extra.id_rol = nuevo_rol
            changed = True
        except Roles.DoesNotExist:
            return Response({"detail": "El rol especificado no existe."}, status=status.HTTP_400_BAD_REQUEST)

    if changed:
        usuario_extra.save()

    payload = serialize(usuario_extra)
    if nuevo_token:
        payload["token"] = nuevo_token

    return Response(payload, status=status.HTTP_200_OK)

