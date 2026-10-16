from calendar import monthrange
from datetime import date

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q

from sports.models import InscripcionDeporte
from services.models import (
    ContratacionTransporte,
    ContratacionComedor,
)

from .models import (
    CuotaMensual,
    Factura,
    DetalleFactura,
)


@transaction.atomic
def generar_factura_alumno(
    alumno,
    mes,
    anio
):

    # -------------------------------------------------
    # 1. Evitar dos facturas del mismo alumno/período
    # -------------------------------------------------

    if Factura.objects.filter(
        alumno=alumno,
        mes=mes,
        anio=anio
    ).exists():

        raise ValidationError(
            "El alumno ya posee una factura "
            "para el período seleccionado."
        )

    # -------------------------------------------------
    # 2. Buscar cuota mensual
    # -------------------------------------------------

    cuota = (
        CuotaMensual.objects
        .filter(
            mes=mes,
            anio=anio,
            estado=True
        )
        .first()
    )

    if not cuota:

        raise ValidationError(
            "No existe una cuota activa "
            "para el período seleccionado."
        )

    # -------------------------------------------------
    # 3. Fechas correspondientes al período
    # -------------------------------------------------

    primer_dia = date(
        anio,
        mes,
        1
    )

    ultimo_dia = date(
        anio,
        mes,
        monthrange(anio, mes)[1]
    )

    # -------------------------------------------------
    # 4. Crear factura
    # -------------------------------------------------

    factura = Factura.objects.create(
        alumno=alumno,
        mes=mes,
        anio=anio,
        fecha_vencimiento=cuota.fecha_vencimiento,
        estado="PENDIENTE"
    )

    # -------------------------------------------------
    # 5. Agregar cuota mensual
    # -------------------------------------------------

    DetalleFactura.objects.create(
        factura=factura,
        tipo_concepto="CUOTA",
        descripcion=(
            f"Cuota mensual "
            f"{cuota.get_mes_display()} "
            f"{cuota.anio}"
        ),
        importe=cuota.valor,
        cuota_mensual=cuota
    )

    # -------------------------------------------------
    # 6. Deportes correspondientes al período
    # -------------------------------------------------

    inscripciones = (
        InscripcionDeporte.objects
        .filter(
            alumno=alumno,
            fecha_inscripcion__lte=ultimo_dia
        )
        .filter(
            Q(fecha_baja__isnull=True)
            |
            Q(fecha_baja__gte=primer_dia)
        )
        .select_related(
            "grupo",
            "grupo__deporte"
        )
    )

    deportes_agregados = set()

    for inscripcion in inscripciones:

        deporte = inscripcion.grupo.deporte

        # Evitamos cobrar dos veces el mismo deporte
        if deporte.pk in deportes_agregados:
            continue

        if deporte.valor_mensual <= 0:

            raise ValidationError(
                f"El deporte {deporte.nombre} "
                "no posee un valor mensual válido."
            )

        DetalleFactura.objects.create(
            factura=factura,
            tipo_concepto="DEPORTE",
            descripcion=(
                f"Deporte: {deporte.nombre}"
            ),
            importe=deporte.valor_mensual,
            grupo_deportivo=inscripcion.grupo
        )

        deportes_agregados.add(
            deporte.pk
        )

    # -------------------------------------------------
    # 7. Transporte contratado para ese mes
    # -------------------------------------------------

    transporte = (
        ContratacionTransporte.objects
        .filter(
            alumno=alumno,
            mes=mes,
            anio=anio,
            estado=True
        )
        .select_related(
            "ruta"
        )
        .first()
    )

    if transporte:

        if transporte.ruta.valor_mensual <= 0:

            raise ValidationError(
                "La ruta de transporte "
                "no posee un valor mensual válido."
            )

        DetalleFactura.objects.create(
            factura=factura,
            tipo_concepto="TRANSPORTE",
            descripcion=(
                f"Transporte: "
                f"{transporte.ruta.nombre}"
            ),
            importe=transporte.ruta.valor_mensual,
            ruta_transporte=transporte.ruta
        )

    # -------------------------------------------------
    # 8. Comedor contratado para ese mes
    # -------------------------------------------------

    comedor = (
        ContratacionComedor.objects
        .filter(
            alumno=alumno,
            mes=mes,
            anio=anio,
            estado=True
        )
        .select_related(
            "servicio"
        )
        .first()
    )

    if comedor:

        if comedor.servicio.valor_mensual <= 0:

            raise ValidationError(
                "El servicio de comedor "
                "no posee un valor mensual válido."
            )

        DetalleFactura.objects.create(
            factura=factura,
            tipo_concepto="COMEDOR",
            descripcion=(
                f"Comedor: "
                f"{comedor.servicio.nombre}"
            ),
            importe=comedor.servicio.valor_mensual,
            servicio_comedor=comedor.servicio
        )

    return factura