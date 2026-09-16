from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from .models import PerfilUsuario


def admin_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        # Primero comprobamos si inició sesión
        if not request.user.is_authenticated:
            messages.error(
                request,
                "Debe iniciar sesión para acceder."
            )

            return redirect("login")

        # Comprobamos que tenga PerfilUsuario
        try:
            perfil = request.user.perfil

        except PerfilUsuario.DoesNotExist:
            messages.error(
                request,
                "Su usuario no tiene un perfil asignado."
            )

            return redirect("login")

        # Comprobamos que realmente sea ADMIN
        if perfil.rol != PerfilUsuario.Rol.ADMIN:

            messages.error(
                request,
                "No tiene permisos para acceder a esta sección."
            )

            return redirect("inicio_por_rol")

        return view_func(
            request,
            *args,
            **kwargs
        )

    return wrapper

def alumno_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            messages.error(
                request,
                "Debe iniciar sesión para acceder."
            )
            return redirect("login")

        try:
            perfil = request.user.perfil

        except PerfilUsuario.DoesNotExist:
            messages.error(
                request,
                "Su usuario no tiene un perfil asignado."
            )
            return redirect("login")

        if perfil.rol != PerfilUsuario.Rol.ALUMNO:
            messages.error(
                request,
                "No tiene permisos para acceder a esta sección."
            )
            return redirect("inicio_por_rol")

        return view_func(
            request,
            *args,
            **kwargs
        )

    return wrapper

def docente_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:

            messages.error(
                request,
                "Debe iniciar sesión para acceder."
            )

            return redirect("login")

        try:
            perfil = request.user.perfil

        except PerfilUsuario.DoesNotExist:

            messages.error(
                request,
                "Su usuario no tiene un perfil asignado."
            )

            return redirect("login")

        if perfil.rol != PerfilUsuario.Rol.DOCENTE:

            messages.error(
                request,
                "No tiene permisos para acceder a esta sección."
            )

            return redirect("inicio_por_rol")

        return view_func(
            request,
            *args,
            **kwargs
        )

    return wrapper