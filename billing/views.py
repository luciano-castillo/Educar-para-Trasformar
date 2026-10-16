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
)

from .forms import (
    CuotaMensualForm,
    GenerarFacturaForm,
)

from .services import generar_factura_alumno


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

@admin_required
def factura_lista(request):

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
