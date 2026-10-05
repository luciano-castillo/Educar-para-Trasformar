from django.urls import path
from . import views


urlpatterns = [

    path(
        "deportes/",
        views.deporte_lista,
        name="deporte_lista"
    ),

    path(
        "deportes/nuevo/",
        views.deporte_crear,
        name="deporte_crear"
    ),

    path(
        "deportes/<int:id_deporte>/editar/",
        views.deporte_editar,
        name="deporte_editar"
    ),

    path(
        "deportes/<int:id_deporte>/desactivar/",
        views.deporte_desactivar,
        name="deporte_desactivar"
    ),
    path(
        "grupos/",
        views.grupo_lista,
        name="grupo_lista"
    ),

    path(
        "grupos/nuevo/",
        views.grupo_crear,
        name="grupo_crear"
    ),

    path(
        "grupos/<int:id_grupo>/editar/",
        views.grupo_editar,
        name="grupo_editar"
    ),
    
    path(
        "grupos/<int:id_grupo>/desactivar/",
        views.grupo_desactivar,
        name="grupo_desactivar"
    ),
    
    path(
        "inscripciones/",
        views.inscripcion_lista,
        name="inscripcion_lista"
    ),

    path(
        "inscripciones/nueva/",
        views.inscripcion_crear,
        name="inscripcion_crear"
    ),

    path(
        "inscripciones/<int:id_inscripcion>/desactivar/",
        views.inscripcion_desactivar,
        name="inscripcion_desactivar"
    ),

]