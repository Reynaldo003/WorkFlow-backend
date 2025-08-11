from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from core.models import Tableros, Equipos, Plantillas
from django.shortcuts import get_object_or_404

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def crear_tablero(request):
    """
    Crea un tablero usando la estructura de una plantilla existente.
    """
    titulo = request.data.get("titulo")
    descripcion = request.data.get("descripcion", "")
    id_equipo = request.data.get("id_equipo")
    id_plantilla = request.data.get("id_plantilla", 1)  # si no envía, usa plantilla 1

    if not titulo or not id_equipo:
        return Response({"error": "Título e id_equipo son obligatorios"}, status=status.HTTP_400_BAD_REQUEST)

    equipo = get_object_or_404(Equipos, id_equipo=id_equipo)
    plantilla = get_object_or_404(Plantillas, id_plantilla=id_plantilla)

    tablero = Tableros.objects.create(
        titulo=titulo,
        descripcion=descripcion,
        id_equipo=equipo,
        id_plantilla=plantilla,
        estructura = {"columns": [], "rows": []}
    )

    return Response({
        "id_tablero": tablero.id_tablero,
        "titulo": tablero.titulo,
        "descripcion": tablero.descripcion,
        "estructura": tablero.estructura
    }, status=status.HTTP_201_CREATED)


@api_view(['PATCH'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def actualizar_estructura_tablero(request, id_tablero):
    tablero = get_object_or_404(Tableros, id_tablero=id_tablero)
    nueva_estructura = request.data.get("estructura")

    if not isinstance(nueva_estructura, dict):
        return Response({"error": "La estructura debe ser un objeto JSON"}, status=status.HTTP_400_BAD_REQUEST)

    tablero.estructura = nueva_estructura
    tablero.save()
    return Response({"msg": "Estructura actualizada"})


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def obtener_tablero(request, id_tablero):
    tablero = get_object_or_404(Tableros, id_tablero=id_tablero)
    return Response({
        "id_tablero": tablero.id_tablero,
        "titulo": tablero.titulo,
        "estructura": tablero.estructura or {"columns": [], "rows": []}
    })


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def listar_tableros_equipo(request, id_equipo):
    equipo = get_object_or_404(Equipos, id_equipo=id_equipo)
    tableros = Tableros.objects.filter(id_equipo=equipo).values(
        "id_tablero", "titulo", "descripcion"
    )
    return Response({"tableros": list(tableros)})
