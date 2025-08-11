from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from core.models import Equipos
from core.models import Equipos, UsuariosEquipos, Usuarios


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def CreaEquipoView(request):
    print(request.data)
    nombre = request.data.get("nombre_equipo")
    descripcion = request.data.get("descripcion")

    if not nombre:
        return Response({"error": "El nombre del equipo es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

    equipo = Equipos.objects.create(
        nombre_equipo=nombre,
        descripcion=descripcion
    )

    # Obtener el usuario desde el token y vincularlo
    usuario = Usuarios.objects.get(user=request.user)
    UsuariosEquipos.objects.create(
        id_usuario=usuario,
        id_equipo=equipo
    )

    return Response({
        "mensaje": "Equipo creado correctamente",
        "equipo": {
            "id": equipo.id_equipo,
            "nombre_equipo": equipo.nombre_equipo,
            "descripcion": equipo.descripcion
        }
    }, status=status.HTTP_201_CREATED)
