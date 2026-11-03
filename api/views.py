from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.response import Response

from academic.models import Tutor
from accounts.models import PerfilUsuario
from billing.models import Factura

from .serializers import (
    AlumnoResumenSerializer,
    FacturaSerializer,
)


@api_view(["GET"])
def estado_api(request):

    return Response(
        {
            "estado": "ok",
            "mensaje": "API móvil disponible",
        }
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def login_mobile(request):

    username = request.data.get("username", "").strip()

    password = request.data.get("password", "")

    if not username or not password:
        return Response(
            {"detail": ("Debe ingresar usuario y contraseña.")},
            status=status.HTTP_400_BAD_REQUEST,
        )

    usuario = authenticate(
        request=request,
        username=username,
        password=password,
    )

    if usuario is None:
        return Response(
            {"detail": ("Usuario o contraseña incorrectos.")},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not usuario.is_active:
        return Response(
            {"detail": ("La cuenta se encuentra inactiva.")},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        perfil = usuario.perfil

    except PerfilUsuario.DoesNotExist:
        return Response(
            {"detail": ("La cuenta no posee un perfil de usuario.")},
            status=status.HTTP_403_FORBIDDEN,
        )

    token, _ = Token.objects.get_or_create(user=usuario)

    return Response(
        {
            "token": token.key,
            "usuario": {
                "id": usuario.id,
                "username": usuario.username,
                "nombre": usuario.first_name,
                "apellido": usuario.last_name,
                "rol": perfil.rol,
                "rol_nombre": (perfil.get_rol_display()),
                "debe_cambiar_password": (perfil.debe_cambiar_password),
            },
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_mobile(request):

    Token.objects.filter(user=request.user).delete()

    return Response({"mensaje": ("Sesión móvil cerrada correctamente.")})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def mis_hijos(request):

    try:
        tutor = Tutor.objects.get(usuario=request.user)

    except Tutor.DoesNotExist:
        return Response(
            {"detail": ("El usuario autenticado no posee un perfil de tutor.")},
            status=status.HTTP_403_FORBIDDEN,
        )

    relaciones = tutor.alumnos_asociados.select_related(
        "alumno",
        "alumno__curso",
        "alumno__curso__nivel",
    )

    alumnos = [relacion.alumno for relacion in relaciones]

    serializer = AlumnoResumenSerializer(alumnos, many=True)

    return Response(
        {
            "tutor": {
                "id_tutor": tutor.id_tutor,
                "nombre": tutor.nombre,
                "apellido": tutor.apellido,
            },
            "hijos": serializer.data,
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def facturas_hijo(
    request,
    id_alumno,
):

    try:
        tutor = Tutor.objects.get(usuario=request.user)

    except Tutor.DoesNotExist:
        return Response(
            {"detail": ("El usuario autenticado no posee un perfil de tutor.")},
            status=status.HTTP_403_FORBIDDEN,
        )

    relacion = (
        tutor.alumnos_asociados.select_related(
            "alumno",
            "alumno__curso",
            "alumno__curso__nivel",
        )
        .filter(alumno_id=id_alumno)
        .first()
    )

    if relacion is None:
        return Response(
            {
                "detail": (
                    "El alumno solicitado "
                    "no se encuentra asociado "
                    "al tutor autenticado."
                )
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    alumno = relacion.alumno

    facturas = Factura.objects.filter(alumno=alumno).prefetch_related(
        "detalles",
        "pagos",
        "pagos__detalles_pago",
    )

    serializer = FacturaSerializer(
        facturas,
        many=True,
    )

    return Response(
        {
            "alumno": {
                "id_alumno": alumno.id_alumno,
                "nombre": alumno.nombre,
                "apellido": alumno.apellido,
                "legajo": alumno.legajo,
            },
            "facturas": serializer.data,
        }
    )
