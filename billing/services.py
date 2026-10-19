from calendar import monthrange
from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.db.models import Sum

from sports.models import InscripcionDeporte
from services.models import (
    ContratacionTransporte,
    ContratacionComedor,
)

from .models import (
    CuotaMensual,
    Factura,
    DetalleFactura,
    Pago,
    PagoDetalle,
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

@transaction.atomic
def registrar_pago(
    factura,
    fecha_transferencia,
    aplicaciones,
    numero_operacion="",
    observaciones="",
    registrado_por=None,
):

    # Bloqueamos la factura mientras
    # registramos el pago.

    factura = (
        Factura.objects
        .select_for_update()
        .get(
            pk=factura.pk
        )
    )

    if factura.estado == "ANULADA":

        raise ValidationError(
            "No se pueden registrar pagos "
            "sobre una factura anulada."
        )

    if not aplicaciones:

        raise ValidationError(
            "Debe seleccionar al menos "
            "un concepto para pagar."
        )

    total_pago = Decimal("0.00")

    aplicaciones_validadas = []

    detalles_usados = set()

    for detalle, importe in aplicaciones:

        importe = Decimal(
            str(importe)
        )

        # -----------------------------------------
        # El detalle debe pertenecer a la factura
        # -----------------------------------------

        if detalle.factura_id != factura.id_factura:

            raise ValidationError(
                "Uno de los conceptos seleccionados "
                "no pertenece a esta factura."
            )

        # -----------------------------------------
        # No repetir el mismo detalle
        # -----------------------------------------

        if detalle.pk in detalles_usados:

            raise ValidationError(
                "Un mismo concepto no puede "
                "repetirse dentro del pago."
            )

        detalles_usados.add(
            detalle.pk
        )

        # -----------------------------------------
        # Importe positivo
        # -----------------------------------------

        if importe <= 0:

            raise ValidationError(
                "El importe aplicado debe "
                "ser mayor a cero."
            )

        # -----------------------------------------
        # Cuánto del concepto ya fue utilizado
        # por pagos VALIDADO o PENDIENTE.
        #
        # RECHAZADOS no cuentan.
        # -----------------------------------------

        utilizado = (
            detalle.aplicaciones_pago
            .exclude(
                pago__estado="RECHAZADO"
            )
            .aggregate(
                total=Sum(
                    "importe_aplicado"
                )
            )["total"]
            or Decimal("0.00")
        )

        disponible = (
            detalle.importe
            - utilizado
        )

        if importe > disponible:

            raise ValidationError(
                f"El importe ingresado para "
                f"'{detalle.descripcion}' "
                f"supera el saldo disponible "
                f"del concepto (${disponible})."
            )

        aplicaciones_validadas.append(
            (
                detalle,
                importe,
            )
        )

        total_pago += importe

    if total_pago <= 0:

        raise ValidationError(
            "El monto del pago debe "
            "ser mayor a cero."
        )

    # ---------------------------------------------
    # Crear pago
    # ---------------------------------------------

    pago = Pago.objects.create(
        factura=factura,
        fecha_transferencia=fecha_transferencia,
        monto=total_pago,
        numero_operacion=numero_operacion,
        observaciones=observaciones,
        registrado_por=registrado_por,
        estado="PENDIENTE"
    )

    # ---------------------------------------------
    # Crear sus aplicaciones
    # ---------------------------------------------

    for detalle, importe in aplicaciones_validadas:

        PagoDetalle.objects.create(
            pago=pago,
            detalle_factura=detalle,
            importe_aplicado=importe
        )

    return pago

@transaction.atomic
def validar_pago(pago):

    pago = (
        Pago.objects
        .select_for_update()
        .select_related(
            "factura"
        )
        .get(
            pk=pago.pk
        )
    )

    factura = (
        Factura.objects
        .select_for_update()
        .get(
            pk=pago.factura_id
        )
    )

    if pago.estado != "PENDIENTE":

        raise ValidationError(
            "Solamente se pueden validar "
            "pagos pendientes."
        )

    if factura.estado == "ANULADA":

        raise ValidationError(
            "No se puede validar un pago "
            "de una factura anulada."
        )

    detalles_pago = (
        pago.detalles_pago
        .select_related(
            "detalle_factura"
        )
        .all()
    )

    if not detalles_pago.exists():

        raise ValidationError(
            "El pago no posee conceptos asociados."
        )

    total_aplicado = Decimal("0.00")

    for pago_detalle in detalles_pago:

        detalle = (
            pago_detalle.detalle_factura
        )

        # El detalle debe pertenecer
        # a la misma factura.

        if detalle.factura_id != factura.id_factura:

            raise ValidationError(
                "El pago contiene un concepto "
                "que pertenece a otra factura."
            )

        ya_pagado = (
            detalle.aplicaciones_pago
            .filter(
                pago__estado="VALIDADO"
            )
            .exclude(
                pago=pago
            )
            .aggregate(
                total=Sum(
                    "importe_aplicado"
                )
            )["total"]
            or Decimal("0.00")
        )

        if (
            ya_pagado
            + pago_detalle.importe_aplicado
            > detalle.importe
        ):

            raise ValidationError(
                f"El pago supera el saldo "
                f"del concepto "
                f"'{detalle.descripcion}'."
            )

        total_aplicado += (
            pago_detalle.importe_aplicado
        )

    # ---------------------------------------------
    # El monto del pago tiene que coincidir
    # con lo distribuido entre conceptos.
    # ---------------------------------------------

    if total_aplicado != pago.monto:

        raise ValidationError(
            "El monto del pago no coincide "
            "con la suma de sus conceptos."
        )

    pago.estado = "VALIDADO"

    pago.save(
        update_fields=[
            "estado"
        ]
    )

    factura.actualizar_estado_pago()

    return pago

@transaction.atomic
def rechazar_pago(pago):

    pago = (
        Pago.objects
        .select_for_update()
        .select_related(
            "factura"
        )
        .get(
            pk=pago.pk
        )
    )

    if pago.estado != "PENDIENTE":

        raise ValidationError(
            "Solamente se pueden rechazar "
            "pagos pendientes."
        )

    pago.estado = "RECHAZADO"

    pago.save(
        update_fields=[
            "estado"
        ]
    )

    pago.factura.actualizar_estado_pago()

    return pago