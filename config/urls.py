from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

    path(
        "admin/",
        admin.site.urls
    ),

    # ==========================================
    # PÁGINA WEB PÚBLICA
    # ==========================================

    path(
        "",
        include("website.urls")
    ),

    # ==========================================
    # SISTEMA DE GESTIÓN
    # ==========================================

    path(
        "academico/",
        include("academic.urls")
    ),

    path(
        "cuentas/",
        include("accounts.urls")
    ),

    # Deportes

    path(
        "",
        include("sports.urls")
    ),

    # Servicios

    path(
        "",
        include("services.urls")
    ),

    # Cuotas / Facturación

    path(
        "",
        include("billing.urls")
    ),

]


if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )