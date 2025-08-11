from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.models import Equipos, UsuariosEquipos, Usuarios
from django.shortcuts import get_object_or_404

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def lista_equipos(request):
    usuario = get_object_or_404(Usuarios, user=request.user)

    # Buscar equipos donde esté en la tabla intermedia
    equipos = Equipos.objects.filter(
        usuariosequipos__id_usuario=usuario.id_usuario
    ).values('id_equipo', 'nombre_equipo', 'descripcion', 'fecha_creacion')

    return Response({"equipos": list(equipos)})
