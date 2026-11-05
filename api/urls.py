from django.urls import path

from .views import (
    estado_api,
    facturas_hijo,
    historial_pagos_hijo,
    login_mobile,
    logout_mobile,
    mis_hijos,
    pagos_factura,
    registrar_pago_mobile,
    resumen_financiero_hijo,
)

app_name = "api"


urlpatterns = [
    path("", estado_api, name="estado"),
    path(
        "login/",
        login_mobile,
        name="login_mobile",
    ),
    path(
        "logout/",
        logout_mobile,
        name="logout_mobile",
    ),
    path("mis-hijos/", mis_hijos, name="mis_hijos"),
    path(
        "mis-hijos/<int:id_alumno>/facturas/",
        facturas_hijo,
        name="facturas_hijo",
    ),
    path(
        ("mis-hijos/<int:id_alumno>/facturas/<int:id_factura>/pagos/"),
        pagos_factura,
        name="pagos_factura",
    ),
    path(
        ("mis-hijos/<int:id_alumno>/facturas/<int:id_factura>/registrar-pago/"),
        registrar_pago_mobile,
        name="registrar_pago_mobile",
    ),
    path(
        ("mis-hijos/<int:id_alumno>/resumen-financiero/"),
        resumen_financiero_hijo,
        name="resumen_financiero_hijo",
    ),
    path(
        ("mis-hijos/<int:id_alumno>/historial-pagos/"),
        historial_pagos_hijo,
        name="historial_pagos_hijo",
    ),
]
