import json
from datetime import date
from decimal import Decimal

from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import (
    api_view,
    parser_classes,
    permission_classes,
)
from rest_framework.parsers import (
    FormParser,
    MultiPartParser,
)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.response import Response

from academic.models import Tutor
from accounts.models import PerfilUsuario
from billing.models import (
    DetalleFactura,
    Factura,
    Pago,
)
from billing.services import (
    actualizar_facturas_vencidas,
    registrar_pago,
)

from .serializers import (
    AlumnoResumenSerializer,
    FacturaSerializer,
    PagoSerializer,
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

    if perfil.rol != PerfilUsuario.Rol.TUTOR:
        return Response(
            {
                "detail": (
                    "El acceso móvil está disponible únicamente para padres o tutores."
                )
            },
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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def resumen_financiero_hijo(
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
        tutor.alumnos_asociados.select_related("alumno")
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

    actualizar_facturas_vencidas()

    alumno = relacion.alumno

    facturas = Factura.objects.filter(alumno=alumno).prefetch_related(
        "detalles",
        "pagos",
        "pagos__detalles_pago",
    )

    total_facturado = Decimal("0.00")
    total_pagado = Decimal("0.00")
    deuda_actual = Decimal("0.00")

    cantidades = {
        "PENDIENTE": 0,
        "PARCIAL": 0,
        "PAGADA": 0,
        "VENCIDA": 0,
        "ANULADA": 0,
    }

    historial_deuda = []

    for factura in facturas:
        cantidades[factura.estado] += 1

        if factura.estado == "ANULADA":
            continue

        total_facturado += factura.total
        total_pagado += factura.total_pagado
        deuda_actual += factura.saldo

        if factura.saldo > 0:
            historial_deuda.append(
                {
                    "id_factura": (factura.id_factura),
                    "mes": factura.mes,
                    "mes_nombre": (factura.get_mes_display()),
                    "anio": factura.anio,
                    "fecha_vencimiento": (factura.fecha_vencimiento),
                    "estado": factura.estado,
                    "estado_nombre": (factura.get_estado_display()),
                    "total": str(factura.total),
                    "total_pagado": str(factura.total_pagado),
                    "saldo": str(factura.saldo),
                }
            )

    return Response(
        {
            "alumno": {
                "id_alumno": alumno.id_alumno,
                "nombre": alumno.nombre,
                "apellido": alumno.apellido,
                "legajo": alumno.legajo,
            },
            "resumen": {
                "total_facturado": str(total_facturado),
                "total_pagado": str(total_pagado),
                "deuda_actual": str(deuda_actual),
                "cantidad_facturas": (facturas.count()),
                "pendientes": cantidades["PENDIENTE"],
                "parciales": cantidades["PARCIAL"],
                "pagadas": cantidades["PAGADA"],
                "vencidas": cantidades["VENCIDA"],
                "anuladas": cantidades["ANULADA"],
            },
            "historial_deuda": (historial_deuda),
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def pagos_factura(
    request,
    id_alumno,
    id_factura,
):
    try:
        tutor = Tutor.objects.get(usuario=request.user)

    except Tutor.DoesNotExist:
        return Response(
            {"detail": ("El usuario autenticado no posee un perfil de tutor.")},
            status=status.HTTP_403_FORBIDDEN,
        )

    relacion = (
        tutor.alumnos_asociados.filter(alumno_id=id_alumno)
        .select_related("alumno")
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

    factura = (
        Factura.objects.filter(
            id_factura=id_factura,
            alumno=relacion.alumno,
        )
        .prefetch_related(
            "pagos__detalles_pago__detalle_factura",
            "pagos__comprobantes",
        )
        .first()
    )

    if factura is None:
        return Response(
            {"detail": ("La factura solicitada no pertenece al alumno.")},
            status=status.HTTP_404_NOT_FOUND,
        )

    pagos = factura.pagos.all()

    serializer = PagoSerializer(
        pagos,
        many=True,
        context={
            "request": request,
        },
    )

    return Response(
        {
            "factura": {
                "id_factura": factura.id_factura,
                "estado": factura.estado,
                "total": str(factura.total),
                "total_pagado": str(factura.total_pagado),
                "saldo": str(factura.saldo),
            },
            "pagos": serializer.data,
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def historial_pagos_hijo(
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
        tutor.alumnos_asociados.select_related("alumno")
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

    pagos = (
        Pago.objects.filter(factura__alumno=alumno)
        .select_related("factura")
        .prefetch_related(
            "detalles_pago__detalle_factura",
            "comprobantes",
        )
        .order_by("-fecha_registro")
    )

    serializer = PagoSerializer(
        pagos,
        many=True,
        context={
            "request": request,
        },
    )

    return Response(
        {
            "alumno": {
                "id_alumno": alumno.id_alumno,
                "nombre": alumno.nombre,
                "apellido": alumno.apellido,
                "legajo": alumno.legajo,
            },
            "cantidad_pagos": pagos.count(),
            "pagos": serializer.data,
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def registrar_pago_mobile(
    request,
    id_alumno,
    id_factura,
):
    try:
        tutor = Tutor.objects.get(usuario=request.user)

    except Tutor.DoesNotExist:
        return Response(
            {"detail": ("El usuario autenticado no posee un perfil de tutor.")},
            status=status.HTTP_403_FORBIDDEN,
        )

    relacion = (
        tutor.alumnos_asociados.select_related("alumno")
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

    factura = (
        Factura.objects.filter(
            id_factura=id_factura,
            alumno=relacion.alumno,
        )
        .prefetch_related("detalles")
        .first()
    )

    if factura is None:
        return Response(
            {"detail": ("La factura solicitada no pertenece al alumno.")},
            status=status.HTTP_404_NOT_FOUND,
        )

    if factura.estado == "ANULADA":
        return Response(
            {"detail": ("No se pueden registrar pagos sobre una factura anulada.")},
            status=status.HTTP_400_BAD_REQUEST,
        )

    fecha_texto = request.data.get(
        "fecha_transferencia",
        "",
    )

    try:
        fecha_transferencia = date.fromisoformat(fecha_texto)

    except ValueError:
        return Response(
            {"detail": ("La fecha de transferencia no es válida.")},
            status=status.HTTP_400_BAD_REQUEST,
        )

    aplicaciones_texto = request.data.get(
        "aplicaciones",
        "",
    )

    try:
        aplicaciones_data = json.loads(aplicaciones_texto)

    except (
        json.JSONDecodeError,
        TypeError,
    ):
        return Response(
            {"detail": ("Los conceptos del pago no poseen un formato válido.")},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not isinstance(
        aplicaciones_data,
        list,
    ):
        return Response(
            {"detail": ("Debe enviar una lista de conceptos a pagar.")},
            status=status.HTTP_400_BAD_REQUEST,
        )

    aplicaciones = []

    for item in aplicaciones_data:
        try:
            id_detalle = int(item["id_detalle"])

            importe = item["importe"]

        except (
            KeyError,
            TypeError,
            ValueError,
        ):
            return Response(
                {"detail": ("Uno de los conceptos del pago es inválido.")},
                status=(status.HTTP_400_BAD_REQUEST),
            )

        detalle = DetalleFactura.objects.filter(
            id_detalle=id_detalle,
            factura=factura,
        ).first()

        if detalle is None:
            return Response(
                {"detail": ("Uno de los conceptos no pertenece a la factura.")},
                status=(status.HTTP_400_BAD_REQUEST),
            )

        aplicaciones.append(
            (
                detalle,
                importe,
            )
        )

    comprobantes = request.FILES.getlist("comprobantes")

    if not comprobantes:
        return Response(
            {"detail": ("Debe adjuntar al menos un comprobante.")},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        pago = registrar_pago(
            factura=factura,
            fecha_transferencia=(fecha_transferencia),
            aplicaciones=aplicaciones,
            numero_operacion=(
                request.data.get(
                    "numero_operacion",
                    "",
                )
            ),
            observaciones=(
                request.data.get(
                    "observaciones",
                    "",
                )
            ),
            registrado_por=request.user,
            comprobantes=comprobantes,
        )

    except ValidationError as error:
        return Response(
            {
                "detail": error.messages[0],
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = PagoSerializer(
        pago,
        context={
            "request": request,
        },
    )

    return Response(
        {
            "mensaje": ("El pago fue registrado y quedó pendiente de validación."),
            "pago": serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )
