import secrets
import string

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.text import slugify

from .models import PerfilUsuario


def _generar_username(
    persona,
    rol
):

    prefijos = {
        PerfilUsuario.Rol.ALUMNO: "alu",
        PerfilUsuario.Rol.DOCENTE: "doc",
        PerfilUsuario.Rol.TUTOR: "tut",
    }

    prefijo = prefijos.get(rol)

    if not prefijo:

        raise ValidationError(
            "No se puede generar una cuenta para este rol."
        )

    identificador = (
        getattr(
            persona,
            "legajo",
            None
        )
        or
        getattr(
            persona,
            "dni",
            None
        )
    )

    identificador = slugify(
        str(identificador)
    ).replace(
        "-",
        ""
    )

    base = (
        f"{prefijo}_{identificador}"
    )

    candidato = base[:150]

    contador = 2

    while User.objects.filter(
        username__iexact=candidato
    ).exists():

        sufijo = (
            f"_{contador}"
        )

        candidato = (
            f"{base[:150 - len(sufijo)]}"
            f"{sufijo}"
        )

        contador += 1

    return candidato


def _generar_password_temporal(
    longitud=14
):

    mayusculas = (
        string.ascii_uppercase
    )

    minusculas = (
        string.ascii_lowercase
    )

    numeros = (
        string.digits
    )

    especiales = (
        "!@#$%&*"
    )

    todos = (
        mayusculas
        + minusculas
        + numeros
        + especiales
    )

    caracteres = [
        secrets.choice(
            mayusculas
        ),
        secrets.choice(
            minusculas
        ),
        secrets.choice(
            numeros
        ),
        secrets.choice(
            especiales
        ),
    ]

    caracteres.extend(
        secrets.choice(
            todos
        )
        for _ in range(
            longitud - 4
        )
    )

    secrets.SystemRandom().shuffle(
        caracteres
    )

    return "".join(
        caracteres
    )


@transaction.atomic
def crear_cuenta_acceso(
    *,
    persona,
    rol
):

    if not persona.estado:

        raise ValidationError(
            
                "No se puede crear una cuenta "
                "para una persona inactiva."
            
        )


    if persona.usuario_id:

        raise ValidationError(
            
                "Esta persona ya posee "
                "una cuenta de acceso."
            
        )


    correo = (
        persona.correo
        or ""
    ).strip().lower()


    if not correo:

        raise ValidationError(
            
                "La persona debe tener "
                "un correo electrónico registrado."
            
        )


    if User.objects.filter(
        email__iexact=correo
    ).exists():

        raise ValidationError(
            
                "El correo electrónico ya está "
                "asociado a otra cuenta de acceso."
            
        )


    username = (
        _generar_username(
            persona,
            rol
        )
    )


    password_temporal = (
        _generar_password_temporal()
    )


    usuario = (
        User.objects.create_user(
            username=username,
            email=correo,
            password=password_temporal,
            first_name=persona.nombre,
            last_name=persona.apellido,
        )
    )


    PerfilUsuario.objects.create(
        usuario=usuario,
        rol=rol,
        debe_cambiar_password=True,
    )


    persona.usuario = usuario

    persona.save(
        update_fields=[
            "usuario"
        ]
    )


    return (
        usuario,
        password_temporal
    )

@transaction.atomic
def restablecer_password_acceso(
    *,
    persona
):

    if not persona.estado:

        raise ValidationError(
            
                "No se puede restablecer la contraseña "
                "de una persona inactiva."
            
        )


    if not persona.usuario_id:

        raise ValidationError(
            
                "Esta persona todavía no posee "
                "una cuenta de acceso."
            
        )


    usuario = persona.usuario


    try:

        perfil = usuario.perfil

    except PerfilUsuario.DoesNotExist:

        raise ValidationError(
            
                "La cuenta no posee "
                "un perfil de usuario asociado."
            
        )


    password_temporal = (
        _generar_password_temporal()
    )


    usuario.set_password(
        password_temporal
    )

    usuario.is_active = True

    usuario.save(
        update_fields=[
            "password",
            "is_active",
        ]
    )


    perfil.debe_cambiar_password = True

    perfil.save(
        update_fields=[
            "debe_cambiar_password"
        ]
    )


    return (
        usuario,
        password_temporal
    )