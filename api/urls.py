from django.urls import path

from .views import (
    estado_api,
    facturas_hijo,
    login_mobile,
    logout_mobile,
    mis_hijos,
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
]
