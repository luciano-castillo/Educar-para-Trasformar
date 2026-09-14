from django.urls import path
from . import views


urlpatterns = [

    path(
        "alumnos/",
        views.alumno_lista,
        name="alumno_lista"
    ),

    path(
        "alumnos/nuevo/",
        views.alumno_crear,
        name="alumno_crear"
    ),

    path(
        "alumnos/<int:id_alumno>/editar/",
        views.alumno_editar,
        name="alumno_editar"
    ),

    path(
        "alumnos/<int:id_alumno>/desactivar/",
        views.alumno_desactivar,
        name="alumno_desactivar"
    ),
    
    path(
        "alumno/mis-datos/",
        views.alumno_mis_datos,
        name="alumno_mis_datos"
    ),

    path(
        "alumno/mis-datos/editar/",
        views.alumno_editar_mis_datos,
        name="alumno_editar_mis_datos"
    ),

]