from django.contrib import admin
from django.urls import path
from crea_equipo.views import CreaEquipoView
from login.views import login, profile
from register.views import register
from lista_equipos.views import lista_equipos
from tableros.views import crear_tablero, obtener_tablero, actualizar_estructura_tablero, listar_tableros_equipo
from invitar.views import invitar_usuario

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cequipo/', CreaEquipoView),
    path('lista_equipos/', lista_equipos),
    path('login/', login),
    path('register/', register),
    path('profile', profile),
    path('tablero/', crear_tablero),
    path('tablero/<int:id_tablero>/', obtener_tablero),
    path('tablero/<int:id_tablero>/estructura/', actualizar_estructura_tablero),
    path('equipos/<int:id_equipo>/tableros/', listar_tableros_equipo),
    path('invitar/<int:id_equipo>', invitar_usuario),
]
