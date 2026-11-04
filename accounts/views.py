from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    login,
    logout,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from academic.models import (
    Alumno,
    Profesor,
    Tutor,
)
from accounts.decorators import admin_required

from .forms import CambioPasswordInicialForm
from .models import PerfilUsuario
from .services import (
    crear_cuenta_acceso,
    restablecer_password_acceso,
)


def login_usuario(request):

    perfil_seleccionado = (
        request.GET.get("perfil")
        or request.POST.get("perfil")
        or ""
    ).upper()

    roles_validos = dict(PerfilUsuario.Rol.choices)
    perfil_nombre = roles_validos.get(
        perfil_seleccionado,
        ""
    )

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

                        if perfil.debe_cambiar_password:

                            return redirect(
                                "cambiar_password_inicial"
                            )

                        return redirect(
                            "inicio_por_rol"
                        )

    return render(
        request,
        "accounts/login.html",
        {
            "perfil_seleccionado": perfil_seleccionado,
            "perfil_nombre": perfil_nombre,
            "roles_validos": roles_validos,
        }
    )


@login_required
def inicio_por_rol(request):

    try:
        perfil = request.user.perfil
        rol = perfil.rol

    except PerfilUsuario.DoesNotExist:

        logout(request)

        messages.error(
            request,
            "El usuario no tiene un perfil asignado."
        )

        return redirect("login")

    if perfil.debe_cambiar_password:

        return redirect(
            "cambiar_password_inicial"
        )

    if rol == PerfilUsuario.Rol.ADMIN:
        return redirect("admin_dashboard")
    
    if rol == PerfilUsuario.Rol.ALUMNO:
        return redirect("alumno_mis_datos")
    
    if rol == PerfilUsuario.Rol.DOCENTE:
        return redirect("profesor_mis_datos")
    
    if rol == PerfilUsuario.Rol.TUTOR:
        return redirect("tutor_mis_hijos")

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

@login_required
def cambiar_password_inicial(request):

    try:

        perfil = request.user.perfil

    except PerfilUsuario.DoesNotExist:

        logout(request)

        messages.error(
            request,
            "El usuario no tiene un perfil asignado."
        )

        return redirect("login")


    # Si ya realizó el cambio obligatorio,
    # no debe volver a esta pantalla.

    if not perfil.debe_cambiar_password:

        return redirect(
            "inicio_por_rol"
        )


    if request.method == "POST":

        form = CambioPasswordInicialForm(
            request.user,
            request.POST
        )

        if form.is_valid():

            usuario = form.save()

            perfil.debe_cambiar_password = False

            perfil.save(
                update_fields=[
                    "debe_cambiar_password"
                ]
            )

            # Mantiene la sesión abierta después
            # de modificar la contraseña.

            update_session_auth_hash(
                request,
                usuario
            )

            messages.success(
                request,
                (
                    "Tu contraseña fue actualizada "
                    "correctamente."
                )
            )

            return redirect(
                "inicio_por_rol"
            )

    else:

        form = CambioPasswordInicialForm(
            request.user
        )


    return render(
        request,
        "accounts/cambiar_password_inicial.html",
        {
            "form": form,
        }
    )

@admin_required
def admin_dashboard(request):

    return render(
        request,
        "accounts/admin_dashboard.html"
    )
    
def _procesar_creacion_cuenta(
    request,
    *,
    persona,
    rol,
    volver_url
):

    if request.method != "POST":

        return redirect(
            volver_url
        )


    try:

        usuario, password_temporal = (
            crear_cuenta_acceso(
                persona=persona,
                rol=rol,
            )
        )

    except ValidationError as error:

        messages.error(
            request,
            error.messages[0]
        )

        return redirect(
            volver_url
        )


    request.session[
        "credenciales_temporales"
    ] = {
        "nombre": (
            f"{persona.nombre} "
            f"{persona.apellido}"
        ),
        "rol": (
            usuario.perfil
            .get_rol_display()
        ),
        "username": (
            usuario.username
        ),
        "password": (
            password_temporal
        ),
        "volver_url": (
            volver_url
        ),
    }


    return redirect(
        "credenciales_temporales"
    )

def _procesar_restablecimiento_password(
    request,
    *,
    persona,
    volver_url
):

    if request.method != "POST":

        return redirect(
            volver_url
        )


    try:

        usuario, password_temporal = (
            restablecer_password_acceso(
                persona=persona
            )
        )

    except ValidationError as error:

        messages.error(
            request,
            error.messages[0]
        )

        return redirect(
            volver_url
        )


    request.session[
        "credenciales_temporales"
    ] = {
        "nombre": (
            f"{persona.nombre} "
            f"{persona.apellido}"
        ),
        "rol": (
            usuario.perfil
            .get_rol_display()
        ),
        "username": (
            usuario.username
        ),
        "password": (
            password_temporal
        ),
        "volver_url": (
            volver_url
        ),
        "titulo": (
            "Contraseña restablecida correctamente"
        ),
    }


    return redirect(
        "credenciales_temporales"
    )

@admin_required
def restablecer_password_alumno(
    request,
    id_alumno
):

    alumno = get_object_or_404(
        Alumno,
        id_alumno=id_alumno
    )

    return _procesar_restablecimiento_password(
        request,
        persona=alumno,
        volver_url="alumno_lista",
    )


@admin_required
def restablecer_password_profesor(
    request,
    id_profesor
):

    profesor = get_object_or_404(
        Profesor,
        id_profesor=id_profesor
    )

    return _procesar_restablecimiento_password(
        request,
        persona=profesor,
        volver_url="profesor_lista",
    )


@admin_required
def restablecer_password_tutor(
    request,
    id_tutor
):

    tutor = get_object_or_404(
        Tutor,
        id_tutor=id_tutor
    )

    return _procesar_restablecimiento_password(
        request,
        persona=tutor,
        volver_url="tutor_lista",
    )

@admin_required
def crear_cuenta_alumno(
    request,
    id_alumno
):

    alumno = get_object_or_404(
        Alumno,
        id_alumno=id_alumno
    )

    return _procesar_creacion_cuenta(
        request,
        persona=alumno,
        rol=PerfilUsuario.Rol.ALUMNO,
        volver_url="alumno_lista",
    )


@admin_required
def crear_cuenta_profesor(
    request,
    id_profesor
):

    profesor = get_object_or_404(
        Profesor,
        id_profesor=id_profesor
    )

    return _procesar_creacion_cuenta(
        request,
        persona=profesor,
        rol=PerfilUsuario.Rol.DOCENTE,
        volver_url="profesor_lista",
    )


@admin_required
def crear_cuenta_tutor(
    request,
    id_tutor
):

    tutor = get_object_or_404(
        Tutor,
        id_tutor=id_tutor
    )

    return _procesar_creacion_cuenta(
        request,
        persona=tutor,
        rol=PerfilUsuario.Rol.TUTOR,
        volver_url="tutor_lista",
    )


@admin_required
def credenciales_temporales(
    request
):

    credenciales = (
        request.session.pop(
            "credenciales_temporales",
            None
        )
    )


    if not credenciales:

        messages.info(
            request,
            (
                "No existen credenciales "
                "temporales para mostrar."
            )
        )

        return redirect(
            "admin_dashboard"
        )


    return render(
        request,
        "accounts/credenciales_temporales.html",
        {
            "credenciales": (
                credenciales
            )
        }
    )