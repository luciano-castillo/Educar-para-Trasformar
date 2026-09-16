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
    #profesores
    
    path(
        "profesores/",
        views.profesor_lista,
        name="profesor_lista"
    ),

    path(
        "profesores/nuevo/",
        views.profesor_crear,
        name="profesor_crear"
    ),

    path(
        "profesores/<int:id_profesor>/editar/",
        views.profesor_editar,
        name="profesor_editar"
    ),

    path(
        "profesores/<int:id_profesor>/desactivar/",
        views.profesor_desactivar,
        name="profesor_desactivar"
    ),
    
    path(
        "profesor/mis-datos/",
        views.profesor_mis_datos,
        name="profesor_mis_datos"
    ),

    path(
        "profesor/mis-datos/editar/",
        views.profesor_editar_mis_datos,
        name="profesor_editar_mis_datos"
    ),

]
