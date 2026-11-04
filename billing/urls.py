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
    #Facturas
    path(
        "facturas/",
        views.factura_lista,
        name="factura_lista"
    ),

    path(
        "facturas/nueva/",
        views.factura_generar,
        name="factura_generar"
    ),

    path(
        "facturas/<int:id_factura>/",
        views.factura_detalle,
        name="factura_detalle"
    ),
    
    # PAGOS

    path(
        "facturas/<int:id_factura>/pagos/nuevo/",
        views.pago_registrar,
        name="pago_registrar"
    ),

    path(
        "pagos/<int:id_pago>/validar/",
        views.pago_validar,
        name="pago_validar"
    ),

    path(
        "pagos/<int:id_pago>/rechazar/",
        views.pago_rechazar,
        name="pago_rechazar"
    ),
    
    # REPORTES

    path(
        "reportes/pagos/",
        views.reporte_pagos,
        name="reporte_pagos"
    ),
    path(
        "reportes/deportes/",
        views.reporte_deportes,
        name="reporte_deportes"
    ),
    path(
        "reportes/transporte/",
        views.reporte_transporte,
        name="reporte_transporte"
    ),

]