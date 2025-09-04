import secrets
import logging
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db import IntegrityError
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from email.message import EmailMessage
import smtplib

from core.models import Equipos, Usuarios, UsuariosEquipos, Roles

logger = logging.getLogger(__name__)

def _generate_password(length=10):
    return secrets.token_urlsafe(length)[:length]

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def invitar_usuario(request, id_equipo):
    correo = (request.data.get("email") or "").strip().lower()
    nombre = (request.data.get("nombre") or "").strip()
    apellido = (request.data.get("apellido") or "").strip()

    if not correo:
        return Response({"error": "Email requerido"}, status=status.HTTP_400_BAD_REQUEST)

    equipo = get_object_or_404(Equipos, id_equipo=id_equipo)

    try:
        # --- 1) Usuario de Django ---
        user = User.objects.filter(username=correo).first()
        raw_password = None
        if not user:
            raw_password = _generate_password(10)
            user = User.objects.create_user(username=correo, email=correo, password=raw_password)

        # --- 2) Rol por defecto ---
        role = Roles.objects.first() or Roles.objects.create(nombre_rol="Miembro")

        # --- 3) Perfil idempotente por correo ---
        perfil = Usuarios.objects.filter(correo=correo).first()
        if perfil:
            # enlaza al user (cuidando OneToOne)
            if perfil.user_id != user.id:
                # si hubiera otro perfil ya enlazado a este user (raro), resolverlo
                otro = Usuarios.objects.filter(user=user).exclude(pk=perfil.pk).first()
                if otro:
                    # estrategia simple: borrar el duplicado ‘otro’ (ajústalo a tu negocio)
                    otro.delete()
                perfil.user = user
            if nombre:   perfil.nombre = nombre
            if apellido: perfil.apellido = apellido
            if not perfil.id_rol_id:
                perfil.id_rol = role
            # no guardes contraseñas en texto plano:
            # perfil.contrasena = ""  # opcional: deja vacío
            perfil.save()
        else:
            # crear perfil nuevo, cuidando UNIQUE de 'usuario'
            usuario_slug = correo
            if Usuarios.objects.filter(usuario=usuario_slug).exists():
                base = correo.split("@")[0]
                n = 1
                while Usuarios.objects.filter(usuario=f"{base}{n}").exists():
                    n += 1
                usuario_slug = f"{base}{n}"

            perfil = Usuarios.objects.create(
                user=user,
                nombre=nombre or correo.split("@")[0],
                apellido=apellido or "",
                correo=correo,
                usuario=usuario_slug,
                contrasena="",          # NO guardes la contraseña
                id_rol=role
            )

        # --- 4) Relación con el equipo (idempotente) ---
        UsuariosEquipos.objects.get_or_create(id_usuario=perfil, id_equipo=equipo)

    except IntegrityError as ex:
        logger.exception("Integridad de datos al crear/actualizar perfil")
        return Response({"error": "Integridad de datos", "detail": str(ex)}, status=400)
    except Exception as ex:
        logger.exception("Error creando usuario o asociándolo al equipo")
        return Response({"error": "Error al crear usuario", "detail": str(ex)}, status=500)

    remitente = 'workflow2709@gmail.com'
    destinatario = correo
    mensaje = f"""Ha sido invitado al equipo de trabajo: {equipo.nombre_equipo} en WorkFlow.\n
    Su usuario es: {user}
    Su contraseña temporal: {raw_password}
    
    Puede Inciar Sesion aqui: https://work-flow-frontend.vercel.app/loginregistro

    Por seguridad, al iniciar sesion cambie su contraseña."""
    
    if raw_password == None:
        mensaje = f"""Ha sido añadido al equipo de trabajo: {equipo.nombre_equipo} en WorkFlow.\n
        Use sus credenciales de acceso existentes para visualizar su nuevo equipo de trabajo.

        Puede Inciar Sesion aqui: https://work-flow-frontend.vercel.app/loginregistro

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

