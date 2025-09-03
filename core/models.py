from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
import uuid
from django.contrib.auth.models import User
from django.utils import timezone

class Actualizaciones(models.Model):
    id_actualizacion = models.AutoField(primary_key=True)
    id_tarea = models.ForeignKey('Tareas', models.DO_NOTHING, db_column='id_tarea')
    id_usuario = models.ForeignKey('Usuarios', models.DO_NOTHING, db_column='id_usuario')
    mensaje = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'actualizaciones'


class Automatizaciones(models.Model):
    id_automatizacion = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)
    regla = models.JSONField()
    accion = models.JSONField()
    id_tablero = models.ForeignKey('Archivos', models.DO_NOTHING, db_column='id_archivo')

    class Meta:
        managed = False
        db_table = 'automatizaciones'


class Equipos(models.Model):
    id_equipo = models.AutoField(primary_key=True)
    nombre_equipo = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'equipos'


class Notificaciones(models.Model):
    id_notificacion = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey('Usuarios', models.DO_NOTHING, db_column='id_usuario')
    mensaje = models.TextField()
    leido = models.BooleanField()
    fecha = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'notificaciones'


class Plantillas(models.Model):
    id_plantilla = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    estructura = models.JSONField()
    descripcion = models.TextField()

    class Meta:
        managed = False
        db_table = 'plantillas'


class Roles(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre_rol = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'roles'

class Archivos(models.Model):
    id_archivo = models.AutoField(primary_key=True)
    # 'tablero' | 'word' | 'excel'  (puedes ampliar: 'powerbi', etc.)
    tipo = models.CharField(max_length=20)
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField(default="")
    estructura = models.JSONField()                 # HTML (word), AOA (excel), cols/rows (tablero)
    id_equipo = models.ForeignKey('Equipos', models.DO_NOTHING, db_column='id_equipo')
    id_plantilla = models.ForeignKey('Plantillas', models.DO_NOTHING, db_column='id_plantilla', null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'archivos'


class Tareas(models.Model):
    id_tarea = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=100)
    id_tablero = models.ForeignKey('Archivos', models.DO_NOTHING, db_column='id_archivo')
    id_usuario_asignado = models.ForeignKey('Usuarios', models.DO_NOTHING, db_column='id_usuario_asignado')
    datos = models.JSONField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'tareas'


class Usuarios(models.Model):
    id_usuario = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    correo = models.EmailField(unique=True, max_length=60)
    usuario = models.CharField(unique=True, max_length=30)
    contrasena = models.TextField()
    id_rol = models.ForeignKey('Roles', models.DO_NOTHING, db_column='id_rol')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'usuarios'
        managed = False


class UsuariosEquipos(models.Model):
    id = models.AutoField(primary_key=True)  # ahora Django sabe que existe esta PK
    id_usuario = models.ForeignKey(Usuarios, models.DO_NOTHING, db_column='id_usuario')
    id_equipo = models.ForeignKey(Equipos, models.DO_NOTHING, db_column='id_equipo')

    class Meta:
        managed = False
        db_table = 'usuarios_equipos'
