from django.contrib import admin
from django.urls import path
from crea_equipo.views import CreaEquipoView
from login.views import login, profile
from register.views import register
from lista_equipos.views import lista_equipos
from tableros.views import crear_archivo, obtener_archivo, actualizar_estructura_archivo, listar_archivos_equipo
from invitar.views import invitar_usuario

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cequipo/', CreaEquipoView),
    path('lista_equipos/', lista_equipos),
    path('login/', login),
    path('profile/', profile),
    path('register/', register),
    path('archivo/', crear_archivo),
    path('archivo/<int:id_archivo>/', obtener_archivo),
    path('archivo/<int:id_archivo>/estructura/', actualizar_estructura_archivo),
    path('equipos/<int:id_equipo>/tableros/', listar_archivos_equipo),
    path('invitar/<int:id_equipo>', invitar_usuario),
]
