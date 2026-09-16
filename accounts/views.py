from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from .models import PerfilUsuario


def login_usuario(request):

    perfil_seleccionado = (
        request.GET.get("perfil")
        or request.POST.get("perfil")
        or ""
    ).upper()

    roles_validos = dict(PerfilUsuario.Rol.choices)

    if perfil_seleccionado not in roles_validos:
        perfil_seleccionado = ""

    if request.method == "POST":

        identificador = request.POST.get("identificador", "").strip()
        password = request.POST.get("password", "")

        # Permite iniciar sesión usando username o correo.
        usuario = User.objects.filter(
            username__iexact=identificador
        ).first()

        if usuario is None:
            usuario = User.objects.filter(
                email__iexact=identificador
            ).first()

        if usuario is None:
            messages.error(
                request,
                "Usuario o contraseña incorrectos."
            )

        else:

            usuario_autenticado = authenticate(
                request,
                username=usuario.username,
                password=password
            )

            if usuario_autenticado is None:

                messages.error(
                    request,
                    "Usuario o contraseña incorrectos."
                )

            else:

                try:
                    perfil = usuario_autenticado.perfil

                except PerfilUsuario.DoesNotExist:

                    messages.error(
                        request,
                        "El usuario no tiene un perfil asignado."
                    )

                else:

                    if (
                        perfil_seleccionado
                        and perfil.rol != perfil_seleccionado
                    ):

                        messages.error(
                            request,
                            "La cuenta no corresponde al perfil seleccionado."
                        )

                    else:

                        login(
                            request,
                            usuario_autenticado
                        )

                        return redirect("inicio_por_rol")

    return render(
        request,
        "accounts/login.html",
        {
            "perfil_seleccionado": perfil_seleccionado,
            "roles_validos": roles_validos,
        }
    )


@login_required
def inicio_por_rol(request):

    try:
        rol = request.user.perfil.rol

    except PerfilUsuario.DoesNotExist:

        logout(request)

        messages.error(
            request,
            "El usuario no tiene un perfil asignado."
        )

        return redirect("login")

    if rol == PerfilUsuario.Rol.ADMIN:
        return redirect("alumno_lista")
    
    if rol == PerfilUsuario.Rol.ALUMNO:
        return redirect("alumno_mis_datos")
    
    if rol == PerfilUsuario.Rol.DOCENTE:
        return redirect("profesor_mis_datos")

    return render(
        request,
        "accounts/inicio.html",
        {
            "rol": request.user.perfil.get_rol_display()
        }
    )


def logout_usuario(request):

    logout(request)

    return redirect("login")
