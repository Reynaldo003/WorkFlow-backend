# tableros/views_invitar.py
import secrets
import logging
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import requests
from email.message import EmailMessage
import smtplib
from core.models import Equipos, Usuarios, UsuariosEquipos, Roles

#rzbb oxiw vaxo oynt

logger = logging.getLogger(__name__)

def _generate_password(length=10):
    # token_urlsafe genera una cadena segura; recortamos a length
    return secrets.token_urlsafe(length)[:length]

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def invitar_usuario(request, id_equipo):
    correo = (request.data.get("email") or "").strip().lower()
    nombre = request.data.get("nombre", "") or ""
    apellido = request.data.get("apellido", "") or ""
    
    if not correo:
        return Response({"error": "Email requerido"}, status=status.HTTP_400_BAD_REQUEST)
    # validar equipo
    equipo = get_object_or_404(Equipos, id_equipo=id_equipo)

    # Buscar o crear usuario Django
    try:
        user = User.objects.filter(username=correo).first()
        created_user = False
        raw_password = None
        if not user:
            raw_password = _generate_password(10)
            user = User(username=correo, email=correo)
            user.set_password(raw_password)
            user.save()
            created_user = True
        else:
            # no exponemos ni cambiamos password si ya existía
            raw_password = None

        # Asegurarnos de que haya un role por defecto
        role = Roles.objects.first()
        if not role:
            # crear un role por defecto si no existe
            role = Roles.objects.create(nombre_rol="Usuario")

        # Crear o actualizar perfil Usuarios
        perfil, created_perfil = Usuarios.objects.get_or_create(
            user=user,
            defaults={
                "nombre": nombre or correo.split("@")[0],
                "apellido": apellido or "",
                "correo": correo,
                "usuario": correo,
                "contrasena": raw_password or "",
                "id_rol": role
            }
        )
        # Asociar a equipo (UsuariosEquipos)
        # Verificamos si ya existe la relación
        relacion = UsuariosEquipos.objects.filter(id_usuario=perfil, id_equipo=equipo).first()
        if not relacion:
            UsuariosEquipos.objects.create(id_usuario=perfil, id_equipo=equipo)

    except Exception as ex:
        logger.exception("Error creando usuario o asociando al equipo")
        return Response({"error": "Error al crear usuario"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    remitente = 'workflow2709@gmail.com'
    destinatario = correo #puede ser para varios ['','']
    mensaje = f"""Ha sido invitado al equipo de trabajo: {equipo.nombre_equipo} en WorkFlow.\n
    Su usuario es: {user}.
    Su contraseña temporal: {raw_password}
    
    Puede Inciar Sesion aqui: http://localhost:5173/loginregistro

    Por seguridad, al iniciar sesion cambie su contraseña."""
    
    if raw_password == None:
        mensaje = f"""Ha sido añadido al equipo de trabajo: {equipo.nombre_equipo} en WorkFlow.\n
        Use sus credenciales de acceso existentes para visualizar su nuevo equipo de trabajo.

        Puede Inciar Sesion aqui: http://localhost:5173/loginregistro

        Por seguridad, al iniciar sesion cambie su contraseña."""
        
    asunto = "Invitacion a WorkFlow"
    contra = "gntx ppix dzkd cdxt"
    try:
        email = EmailMessage()
        email["From"] = remitente
        email["To"] = destinatario
        email["Subject"] = asunto
        email.set_content(mensaje)

        smtp = smtplib.SMTP_SSL('smtp.gmail.com')
        smtp.login(remitente, contra)
        smtp.sendmail(remitente, destinatario, email.as_string())
        smtp.quit()

    except Exception as ex:
        logger.exception("Error enviando email con el Servicio de Correos")
        return Response({
            "message": "Usuario creado y asociado al equipo, pero ocurrio un error al enviar el correo.",
            "error": str(ex)
        }, status=status.HTTP_207_MULTI_STATUS)
    
    return Response({
        "message": "Usuario invitado y correo enviado correctamente.",
        "email": correo,
        "equipo": equipo.nombre_equipo
    }, status=status.HTTP_200_OK)