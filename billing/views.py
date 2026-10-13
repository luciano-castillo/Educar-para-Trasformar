from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)

from django.contrib import messages

from accounts.decorators import admin_required

from .models import CuotaMensual
from .forms import CuotaMensualForm


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
