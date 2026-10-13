from django.urls import path

from . import views


urlpatterns = [

    path(
        "cuotas/",
        views.cuota_lista,
        name="cuota_lista"
    ),

    path(
        "cuotas/nueva/",
        views.cuota_crear,
        name="cuota_crear"
    ),

    path(
        "cuotas/<int:id_cuota>/editar/",
        views.cuota_editar,
        name="cuota_editar"
    ),

    path(
        "cuotas/<int:id_cuota>/desactivar/",
        views.cuota_desactivar,
        name="cuota_desactivar"
    ),

]