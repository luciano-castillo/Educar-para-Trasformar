from django.urls import path
from . import views


urlpatterns = [

    path(
        "transporte/rutas/",
        views.ruta_lista,
        name="ruta_lista"
    ),

    path(
        "transporte/rutas/nueva/",
        views.ruta_crear,
        name="ruta_crear"
    ),

    path(
        "transporte/rutas/<int:id_ruta>/editar/",
        views.ruta_editar,
        name="ruta_editar"
    ),

    path(
        "transporte/rutas/<int:id_ruta>/desactivar/",
        views.ruta_desactivar,
        name="ruta_desactivar"
    ),
    
    path(
        "transporte/contrataciones/",
        views.transporte_contratacion_lista,
        name="transporte_contratacion_lista"
    ),

    path(
        "transporte/contrataciones/nueva/",
        views.transporte_contratacion_crear,
        name="transporte_contratacion_crear"
    ),

    path(
        "transporte/contrataciones/<int:id_contratacion>/editar/",
        views.transporte_contratacion_editar,
        name="transporte_contratacion_editar"
    ),

    path(
        "transporte/contrataciones/<int:id_contratacion>/desactivar/",
        views.transporte_contratacion_desactivar,
        name="transporte_contratacion_desactivar"
    ),
    
    # COMEDOR

    path(
        "comedor/servicios/",
        views.comedor_lista,
        name="comedor_lista"
    ),

    path(
        "comedor/servicios/nuevo/",
        views.comedor_crear,
        name="comedor_crear"
    ),

    path(
        "comedor/servicios/<int:id_servicio_comedor>/editar/",
        views.comedor_editar,
        name="comedor_editar"
    ),

    path(
        "comedor/servicios/<int:id_servicio_comedor>/desactivar/",
        views.comedor_desactivar,
        name="comedor_desactivar"
    ),

    path(
        "comedor/contrataciones/",
        views.comedor_contratacion_lista,
        name="comedor_contratacion_lista"
    ),

    path(
        "comedor/contrataciones/nueva/",
        views.comedor_contratacion_crear,
        name="comedor_contratacion_crear"
    ),

    path(
        "comedor/contrataciones/<int:id_contratacion>/editar/",
        views.comedor_contratacion_editar,
        name="comedor_contratacion_editar"
    ),

    path(
        "comedor/contrataciones/<int:id_contratacion>/desactivar/",
        views.comedor_contratacion_desactivar,
        name="comedor_contratacion_desactivar"
    ),

]