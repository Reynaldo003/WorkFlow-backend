from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from core.models import Equipos, Plantillas, Archivos
from django.shortcuts import get_object_or_404
# views.py
from django.db import transaction

DEFAULT_PLANTILLA = {
    "word":    2,   # <- pon aquí el id real de la plantilla default para Word
    "excel":   3,   # <- id real para Excel
    "tablero": 1,   # <- id real para Tablero (ej. tu Kanban Básico)
}

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@transaction.atomic
def crear_archivo(request):
    tipo = request.data.get("tipo")
    titulo = request.data.get("titulo")
    descripcion = request.data.get("descripcion", "")
    id_equipo = request.data.get("id_equipo")
    id_plantilla = request.data.get("id_plantilla")

    # Validaciones básicas
    if tipo not in ["word","excel","tablero"] or not titulo or not id_equipo:
        return Response({"error": "Datos inválidos"}, status=400)

    equipo = get_object_or_404(Equipos, id_equipo=id_equipo)

    # Resolver plantilla obligatoria (NOT NULL):
    # 1) Si viene id_plantilla úsalo; 2) si no, usa el default por tipo.
    if not id_plantilla:
        id_plantilla = DEFAULT_PLANTILLA.get(tipo)
        if not id_plantilla:
            return Response({"error": f"No hay plantilla por defecto para tipo={tipo}"}, status=400)

    plantilla = get_object_or_404(Plantillas, id_plantilla=id_plantilla)

    # Opcional: valida que la plantilla sea del tipo esperado (si tu modelo Plantillas tiene campo tipo)
    # if plantilla.tipo != tipo: return Response({"error": "La plantilla no coincide con el tipo"}, status=400)

    # La estructura inicial proviene SIEMPRE de la plantilla seleccionada
    estructura_base = plantilla.estructura

    arc = Archivos.objects.create(
        tipo=tipo,
        titulo=titulo,
        descripcion=descripcion,
        id_equipo=equipo,
        id_plantilla=plantilla,     # <- nunca NULL
        estructura=estructura_base,
    )
    return Response(
        {"id_archivo": arc.id_archivo, "tipo": arc.tipo, "estructura": arc.estructura},
        status=201
    )


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def obtener_archivo(request, id_archivo):
    arc = get_object_or_404(Archivos, id_archivo=id_archivo)
    return Response({
        "id_archivo": arc.id_archivo, "tipo": arc.tipo, "titulo": arc.titulo,
        "descripcion": arc.descripcion, "estructura": arc.estructura
    })


@api_view(['PATCH'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def actualizar_estructura_archivo(request, id_archivo):
    arc = get_object_or_404(Archivos, id_archivo=id_archivo)
    body = request.data.get("estructura")
    if not isinstance(body, dict):
        return Response({"error":"La estructura debe ser JSON"}, status=400)
    arc.estructura = body
    arc.save()
    return Response({"msg":"Estructura actualizada"})


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def listar_archivos_equipo(request, id_equipo):
    qs = Archivos.objects.filter(id_equipo=id_equipo).values(
        "id_archivo", "tipo", "titulo"
    )
    return Response({"archivos": list(qs)})
