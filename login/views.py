from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from login.serializers import UserSerializer
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework import status
from core.models import Usuarios, Roles
from django.contrib.auth.hashers import make_password
import uuid
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny

@api_view(['POST'])
@authentication_classes([TokenAuthentication])   # Validar token DRF
@permission_classes([AllowAny])            # Exigir usuario autenticado
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

