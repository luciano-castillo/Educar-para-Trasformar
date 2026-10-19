from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)

from django.contrib import messages

from accounts.decorators import admin_required

from django.core.exceptions import ValidationError

from .models import (
    CuotaMensual,
    Factura,
    Pago,
)

from .forms import (
    CuotaMensualForm,
    GenerarFacturaForm,
    RegistrarPagoForm,
)

from .services import (
    generar_factura_alumno,
    registrar_pago,
    validar_pago,
    rechazar_pago,
    actualizar_facturas_vencidas,
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