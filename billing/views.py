from decimal import Decimal

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import (
    Count,
    Sum,
)
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from accounts.decorators import admin_required

from .forms import (
    CuotaMensualForm,
    GenerarFacturaForm,
    RegistrarPagoForm,
    ReporteDeportesForm,
    ReportePagosForm,
    ReporteTransporteForm,
)
from .models import (
    CuotaMensual,
    Factura,
    Pago,
    PagoDetalle,
)
from .services import (
    actualizar_facturas_vencidas,
    generar_factura_alumno,
    rechazar_pago,
    registrar_pago,
    validar_pago,
)


#---Cuotas---
@admin_required
def cuota_lista(request):

    cuotas = (
        CuotaMensual.objects
        .all()
        .order_by(
            "-anio",
            "-mes",
        )
    )

    return render(
        request,
        "billing/cuotas/lista.html",
        {
            "cuotas": cuotas
        }
    )


@admin_required
def cuota_crear(request):

    if request.method == "POST":

        form = CuotaMensualForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "La cuota mensual fue registrada correctamente."
            )

            return redirect(
                "cuota_lista"
            )

    else:

        form = CuotaMensualForm()

    return render(
        request,
        "billing/cuotas/formulario.html",
        {
            "form": form,
            "titulo": "Nueva cuota mensual"
        }
    )


@admin_required
def cuota_editar(
    request,
    id_cuota
):

    cuota = get_object_or_404(
        CuotaMensual,
        id_cuota=id_cuota
    )

    if request.method == "POST":

        form = CuotaMensualForm(
            request.POST,
            instance=cuota
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "La cuota mensual fue modificada correctamente."
            )

            return redirect(
                "cuota_lista"
            )

    else:

        form = CuotaMensualForm(
            instance=cuota
        )

    return render(
        request,
        "billing/cuotas/formulario.html",
        {
            "form": form,
            "titulo": "Modificar cuota mensual"
        }
    )


@admin_required
def cuota_desactivar(
    request,
    id_cuota
):

    cuota = get_object_or_404(
        CuotaMensual,
        id_cuota=id_cuota
    )

    if request.method == "POST":

        cuota.estado = False
        cuota.save()

        messages.success(
            request,
            "La cuota mensual fue desactivada correctamente."
        )

    return redirect(
        "cuota_lista"
    )

#---Facturas---
@admin_required
def factura_lista(request):

    actualizar_facturas_vencidas()
    
    facturas = (
        Factura.objects
        .select_related(
            "alumno",
            "alumno__curso",
        )
        .prefetch_related(
            "detalles"
        )
        .order_by(
            "-anio",
            "-mes",
            "alumno__apellido",
            "alumno__nombre",
        )
    )

    return render(
        request,
        "billing/facturas/lista.html",
        {
            "facturas": facturas
        }
    )


@admin_required
def factura_generar(request):

    if request.method == "POST":

        form = GenerarFacturaForm(
            request.POST
        )

        if form.is_valid():

            alumno = form.cleaned_data[
                "alumno"
            ]

            mes = int(
                form.cleaned_data[
                    "mes"
                ]
            )

            anio = form.cleaned_data[
                "anio"
            ]

            try:

                factura = generar_factura_alumno(
                    alumno=alumno,
                    mes=mes,
                    anio=anio
                )

                messages.success(
                    request,
                    "La factura fue generada correctamente."
                )

                return redirect(
                    "factura_detalle",
                    id_factura=factura.id_factura
                )

            except ValidationError as error:

                form.add_error(
                    None,
                    error.messages[0]
                )

    else:

        form = GenerarFacturaForm()

    return render(
        request,
        "billing/facturas/generar.html",
        {
            "form": form
        }
    )


@admin_required
def factura_detalle(request,id_factura):

    actualizar_facturas_vencidas()
    
    factura = get_object_or_404(
        Factura.objects
        .select_related(
            "alumno",
            "alumno__curso",
        )
        .prefetch_related(
            "detalles"
        ),
        id_factura=id_factura
    )

    return render(
        request,
        "billing/facturas/detalle.html",
        {
            "factura": factura
        }
    )

#---Pagos---
@admin_required
def pago_registrar(
    request,
    id_factura
):

    factura = get_object_or_404(
        Factura.objects
        .select_related(
            "alumno"
        )
        .prefetch_related(
            "detalles"
        ),
        id_factura=id_factura
    )

    if factura.estado == "ANULADA":

        messages.error(
            request,
            "No se pueden registrar pagos "
            "sobre una factura anulada."
        )

        return redirect(
            "factura_detalle",
            id_factura=factura.id_factura
        )

    if request.method == "POST":

        form = RegistrarPagoForm(
            request.POST,
            request.FILES,
            factura=factura
        )

        if form.is_valid():

            try:

                pago = registrar_pago(
                    factura=factura,
                    fecha_transferencia=(
                        form.cleaned_data[
                            "fecha_transferencia"
                        ]
                    ),
                    aplicaciones=(
                        form.cleaned_data[
                            "aplicaciones"
                        ]
                    ),
                    numero_operacion=(
                        form.cleaned_data[
                            "numero_operacion"
                        ]
                    ),
                    observaciones=(
                        form.cleaned_data[
                            "observaciones"
                        ]
                    ),
                    registrado_por=request.user,
                    comprobantes=(
                        form.cleaned_data[
                            "comprobantes"
                        ]
                    ),
                )

                messages.success(
                    request,
                    (
                        f"El pago N° "
                        f"{pago.id_pago} "
                        "fue registrado y quedó "
                        "pendiente de validación."
                    )
                )

                return redirect(
                    "factura_detalle",
                    id_factura=factura.id_factura
                )

            except ValidationError as error:

                form.add_error(
                    None,
                    error.messages[0]
                )

    else:

        form = RegistrarPagoForm(
            factura=factura
        )

    return render(
        request,
        "billing/pagos/registrar.html",
        {
            "form": form,
            "factura": factura,
        }
    )


@admin_required
def pago_validar(
    request,
    id_pago
):

    pago = get_object_or_404(
        Pago.objects.select_related(
            "factura"
        ),
        id_pago=id_pago
    )

    if request.method == "POST":

        try:

            validar_pago(
                pago
            )

            messages.success(
                request,
                "El pago fue validado correctamente."
            )

        except ValidationError as error:

            messages.error(
                request,
                error.messages[0]
            )

    return redirect(
        "factura_detalle",
        id_factura=pago.factura_id
    )


@admin_required
def pago_rechazar(
    request,
    id_pago
):

    pago = get_object_or_404(
        Pago.objects.select_related(
            "factura"
        ),
        id_pago=id_pago
    )

    if request.method == "POST":

        try:

            rechazar_pago(
                pago
            )

            messages.success(
                request,
                "El pago fue rechazado."
            )

        except ValidationError as error:

            messages.error(
                request,
                error.messages[0]
            )

    return redirect(
        "factura_detalle",
        id_factura=pago.factura_id
    )

# --- REPORTES ---

@admin_required
def reporte_pagos(request):

    actualizar_facturas_vencidas()

    form = ReportePagosForm(
        request.GET or None
    )

    facturas = (
        Factura.objects
        .select_related(
            "alumno",
            "alumno__curso",
            "alumno__curso__nivel",
        )
        .prefetch_related(
            "detalles",
            "pagos",
        )
        .all()
    )

    if form.is_valid():

        mes = form.cleaned_data.get(
            "mes"
        )

        anio = form.cleaned_data.get(
            "anio"
        )

        alumno = form.cleaned_data.get(
            "alumno"
        )

        estado = form.cleaned_data.get(
            "estado"
        )

        if mes:

            facturas = facturas.filter(
                mes=int(mes)
            )

        if anio:

            facturas = facturas.filter(
                anio=anio
            )

        if alumno:

            facturas = facturas.filter(
                alumno=alumno
            )

        if estado:

            facturas = facturas.filter(
                estado=estado
            )

    facturas = facturas.order_by(
        "-anio",
        "-mes",
        "alumno__apellido",
        "alumno__nombre",
    )

    # -----------------------------------------
    # Totales generales
    # -----------------------------------------

    total_facturado = Decimal("0.00")
    total_pagado = Decimal("0.00")
    total_deuda = Decimal("0.00")

    cantidad_pendientes = 0
    cantidad_parciales = 0
    cantidad_pagadas = 0
    cantidad_vencidas = 0

    for factura in facturas:

        total_facturado += (
            factura.total
        )

        total_pagado += (
            factura.total_pagado
        )

        total_deuda += (
            factura.saldo
        )

        if factura.estado == "PENDIENTE":

            cantidad_pendientes += 1

        elif factura.estado == "PARCIAL":

            cantidad_parciales += 1

        elif factura.estado == "PAGADA":

            cantidad_pagadas += 1

        elif factura.estado == "VENCIDA":

            cantidad_vencidas += 1

    # -----------------------------------------
    # Total efectivamente pagado por concepto
    # -----------------------------------------

    pagos_por_concepto = (
        PagoDetalle.objects
        .filter(
            pago__estado="VALIDADO",
            detalle_factura__factura__in=(
                facturas
            )
        )
        .values(
            "detalle_factura__tipo_concepto"
        )
        .annotate(
            total=Sum(
                "importe_aplicado"
            )
        )
        .order_by(
            "detalle_factura__tipo_concepto"
        )
    )

    conceptos = {
        "CUOTA": Decimal("0.00"),
        "DEPORTE": Decimal("0.00"),
        "TRANSPORTE": Decimal("0.00"),
        "COMEDOR": Decimal("0.00"),
    }

    for fila in pagos_por_concepto:

        conceptos[
            fila[
                "detalle_factura__tipo_concepto"
            ]
        ] = fila["total"]

    contexto = {
        "form": form,
        "facturas": facturas,

        "total_facturado": total_facturado,
        "total_pagado": total_pagado,
        "total_deuda": total_deuda,

        "cantidad_pendientes": (
            cantidad_pendientes
        ),
        "cantidad_parciales": (
            cantidad_parciales
        ),
        "cantidad_pagadas": (
            cantidad_pagadas
        ),
        "cantidad_vencidas": (
            cantidad_vencidas
        ),

        "total_cuotas": conceptos[
            "CUOTA"
        ],
        "total_deportes": conceptos[
            "DEPORTE"
        ],
        "total_transporte": conceptos[
            "TRANSPORTE"
        ],
        "total_comedor": conceptos[
            "COMEDOR"
        ],
    }

    return render(
        request,
        "billing/reportes/pagos.html",
        contexto
    )

@admin_required
def reporte_deportes(request):

    form = ReporteDeportesForm(
        request.GET or None
    )

    pagos_deportes = (
        PagoDetalle.objects
        .filter(
            pago__estado="VALIDADO",
            detalle_factura__tipo_concepto="DEPORTE",
            detalle_factura__grupo_deportivo__isnull=False,
        )
    )

    if form.is_valid():

        mes = form.cleaned_data.get(
            "mes"
        )

        anio = form.cleaned_data.get(
            "anio"
        )

        deporte = form.cleaned_data.get(
            "deporte"
        )

        nivel = form.cleaned_data.get(
            "nivel"
        )

        profesor = form.cleaned_data.get(
            "profesor"
        )

        if mes:

            pagos_deportes = (
                pagos_deportes.filter(
                    detalle_factura__factura__mes=(
                        int(mes)
                    )
                )
            )

        if anio:

            pagos_deportes = (
                pagos_deportes.filter(
                    detalle_factura__factura__anio=(
                        anio
                    )
                )
            )

        if deporte:

            pagos_deportes = (
                pagos_deportes.filter(
                    detalle_factura__grupo_deportivo__deporte=(
                        deporte
                    )
                )
            )

        if nivel:

            pagos_deportes = (
                pagos_deportes.filter(
                    detalle_factura__grupo_deportivo__nivel=(
                        nivel
                    )
                )
            )

        if profesor:

            pagos_deportes = (
                pagos_deportes.filter(
                    detalle_factura__grupo_deportivo__profesor=(
                        profesor
                    )
                )
            )

    total_cobrado = (
        pagos_deportes
        .aggregate(
            total=Sum(
                "importe_aplicado"
            )
        )["total"]
        or Decimal("0.00")
    )

    reporte = (
        pagos_deportes
        .values(
            "detalle_factura__grupo_deportivo__deporte__nombre",
            "detalle_factura__grupo_deportivo__nivel__nombre",
            "detalle_factura__grupo_deportivo__profesor__apellido",
            "detalle_factura__grupo_deportivo__profesor__nombre",
            "detalle_factura__grupo_deportivo__horario__dia_semana",
            "detalle_factura__grupo_deportivo__horario__hora_inicio",
            "detalle_factura__grupo_deportivo__horario__hora_fin",
        )
        .annotate(
            total_cobrado=Sum(
                "importe_aplicado"
            ),
            cantidad_pagos=Count(
                "pago",
                distinct=True
            ),
            cantidad_alumnos=Count(
                "detalle_factura__factura__alumno",
                distinct=True
            ),
        )
        .order_by(
            "detalle_factura__grupo_deportivo__deporte__nombre",
            "detalle_factura__grupo_deportivo__nivel__nombre",
        )
    )

    return render(
        request,
        "billing/reportes/deportes.html",
        {
            "form": form,
            "reporte": reporte,
            "total_cobrado": total_cobrado,
        }
    )

@admin_required
def reporte_transporte(request):

    form = ReporteTransporteForm(
        request.GET or None
    )

    pagos_transporte = (
        PagoDetalle.objects
        .filter(
            pago__estado="VALIDADO",
            detalle_factura__tipo_concepto="TRANSPORTE",
            detalle_factura__ruta_transporte__isnull=False,
        )
    )

    if form.is_valid():

        mes = form.cleaned_data.get(
            "mes"
        )

        anio = form.cleaned_data.get(
            "anio"
        )

        ruta = form.cleaned_data.get(
            "ruta"
        )

        if mes:

            pagos_transporte = (
                pagos_transporte.filter(
                    detalle_factura__factura__mes=(
                        int(mes)
                    )
                )
            )

        if anio:

            pagos_transporte = (
                pagos_transporte.filter(
                    detalle_factura__factura__anio=(
                        anio
                    )
                )
            )

        if ruta:

            pagos_transporte = (
                pagos_transporte.filter(
                    detalle_factura__ruta_transporte=(
                        ruta
                    )
                )
            )

    total_cobrado = (
        pagos_transporte
        .aggregate(
            total=Sum(
                "importe_aplicado"
            )
        )["total"]
        or Decimal("0.00")
    )

    reporte = (
        pagos_transporte
        .values(
            "detalle_factura__ruta_transporte__nombre",
        )
        .annotate(
            total_cobrado=Sum(
                "importe_aplicado"
            ),
            cantidad_pagos=Count(
                "pago",
                distinct=True
            ),
            cantidad_alumnos=Count(
                "detalle_factura__factura__alumno",
                distinct=True
            ),
        )
        .order_by(
            "detalle_factura__ruta_transporte__nombre"
        )
    )

    return render(
        request,
        "billing/reportes/transporte.html",
        {
            "form": form,
            "reporte": reporte,
            "total_cobrado": total_cobrado,
        }
    )