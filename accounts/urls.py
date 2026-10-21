from django.urls import path
from . import views


urlpatterns = [
    path("login/", views.login_usuario, name="login"),
    path("logout/", views.logout_usuario, name="logout"),
    path("inicio/", views.inicio_por_rol, name="inicio_por_rol"),
    path(
        "admin/dashboard/",
        views.admin_dashboard,
        name="admin_dashboard"
    ),
    path(
        "primer-acceso/cambiar-password/",
        views.cambiar_password_inicial,
        name="cambiar_password_inicial"
    ),
    path(
        "admin/cuentas/alumno/<int:id_alumno>/crear/",
        views.crear_cuenta_alumno,
        name="crear_cuenta_alumno"
    ),

    path(
        "admin/cuentas/profesor/<int:id_profesor>/crear/",
        views.crear_cuenta_profesor,
        name="crear_cuenta_profesor"
    ),

    path(
        "admin/cuentas/tutor/<int:id_tutor>/crear/",
        views.crear_cuenta_tutor,
        name="crear_cuenta_tutor"
    ),

    path(
        "admin/cuentas/credenciales/",
        views.credenciales_temporales,
        name="credenciales_temporales"
    ),
    
    path(
        "admin/cuentas/alumno/<int:id_alumno>/restablecer/",
        views.restablecer_password_alumno,
        name="restablecer_password_alumno"
    ),

    path(
        "admin/cuentas/profesor/<int:id_profesor>/restablecer/",
        views.restablecer_password_profesor,
        name="restablecer_password_profesor"
    ),

    path(
        "admin/cuentas/tutor/<int:id_tutor>/restablecer/",
        views.restablecer_password_tutor,
        name="restablecer_password_tutor"
    ),
]