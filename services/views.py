from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)

from django.contrib import messages

from accounts.decorators import admin_required

from .models import RutaTransporte, ContratacionTransporte, ServicioComedor, ContratacionComedor
from .forms import RutaTransporteForm, ContratacionTransporteForm, ServicioComedorForm, ContratacionComedorForm


@admin_required
def ruta_lista(request):

    rutas = (
        RutaTransporte.objects
        .all()
        .order_by("nombre")
    )

    return render(
        request,
        "services/transporte/rutas/lista.html",
        {
            "rutas": rutas
        }
    )

@admin_required
def ruta_crear(request):

    if request.method == "POST":

        form = RutaTransporteForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "La ruta de transporte fue registrada correctamente."
            )

            return redirect(
                "ruta_lista"
            )

    else:

        form = RutaTransporteForm()

    return render(
        request,
        "services/transporte/rutas/formulario.html",
        {
            "form": form,
            "titulo": "Nueva ruta de transporte"
        }
    )

@admin_required
def ruta_editar(
    request,
    id_ruta
):

    ruta = get_object_or_404(
        RutaTransporte,
        id_ruta=id_ruta
    )

    if request.method == "POST":

        form = RutaTransporteForm(
            request.POST,
            instance=ruta
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "La ruta de transporte fue modificada correctamente."
            )

            return redirect(
                "ruta_lista"
            )

    else:

        form = RutaTransporteForm(
            instance=ruta
        )

    return render(
        request,
        "services/transporte/rutas/formulario.html",
        {
            "form": form,
            "titulo": "Modificar ruta de transporte"
        }
    )

@admin_required
def ruta_desactivar(
    request,
    id_ruta
):

    ruta = get_object_or_404(
        RutaTransporte,
        id_ruta=id_ruta
    )

    if request.method == "POST":

        ruta.estado = False
        ruta.save()

        messages.success(
            request,
            "La ruta de transporte fue desactivada correctamente."
        )

    return redirect(
        "ruta_lista"
    )

@admin_required
def transporte_contratacion_lista(request):

    contrataciones = (
        ContratacionTransporte.objects
        .select_related(
            "alumno",
            "ruta",
            "alumno__curso",
            "alumno__curso__nivel",
        )
        .order_by(
            "-anio",
            "-mes",
            "alumno__apellido",
        )
    )

    return render(
        request,
        "services/transporte/contrataciones/lista.html",
        {
            "contrataciones": contrataciones
        }
    )

@admin_required
def transporte_contratacion_crear(request):

    if request.method == "POST":

        form = ContratacionTransporteForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "La contratación de transporte "
                "fue registrada correctamente."
            )

            return redirect(
                "transporte_contratacion_lista"
            )

    else:

        form = ContratacionTransporteForm()

    return render(
        request,
        "services/transporte/contrataciones/formulario.html",
        {
            "form": form,
            "titulo": "Nueva contratación de transporte"
        }
    )

@admin_required
def transporte_contratacion_editar(
    request,
    id_contratacion
):

    contratacion = get_object_or_404(
        ContratacionTransporte,
        id_contratacion=id_contratacion
    )

    if request.method == "POST":

        form = ContratacionTransporteForm(
            request.POST,
            instance=contratacion
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "La contratación fue modificada correctamente."
            )

            return redirect(
                "transporte_contratacion_lista"
            )

    else:

        form = ContratacionTransporteForm(
            instance=contratacion
        )

    return render(
        request,
        "services/transporte/contrataciones/formulario.html",
        {
            "form": form,
            "titulo": "Modificar contratación"
        }
    )

@admin_required
def transporte_contratacion_desactivar(
    request,
    id_contratacion
):

    contratacion = get_object_or_404(
        ContratacionTransporte,
        id_contratacion=id_contratacion
    )

    if request.method == "POST":

        contratacion.estado = False
        contratacion.save()

        messages.success(
            request,
            "La contratación fue cancelada correctamente."
        )

    return redirect(
        "transporte_contratacion_lista"
    )
    
#COMEDOR
@admin_required
def comedor_lista(request):

    servicios = (
        ServicioComedor.objects
        .all()
        .order_by("nombre")
    )

    return render(
        request,
        "services/comedor/servicios/lista.html",
        {
            "servicios": servicios
        }
    )

@admin_required
def comedor_crear(request):

    if request.method == "POST":

        form = ServicioComedorForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "El servicio de comedor fue registrado correctamente."
            )

            return redirect(
                "comedor_lista"
            )

    else:

        form = ServicioComedorForm()

    return render(
        request,
        "services/comedor/servicios/formulario.html",
        {
            "form": form,
            "titulo": "Nuevo servicio de comedor"
        }
    )

@admin_required
def comedor_editar(
    request,
    id_servicio_comedor
):

    servicio = get_object_or_404(
        ServicioComedor,
        id_servicio_comedor=id_servicio_comedor
    )

    if request.method == "POST":

        form = ServicioComedorForm(
            request.POST,
            instance=servicio
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "El servicio de comedor fue modificado correctamente."
            )

            return redirect(
                "comedor_lista"
            )

    else:

        form = ServicioComedorForm(
            instance=servicio
        )

    return render(
        request,
        "services/comedor/servicios/formulario.html",
        {
            "form": form,
            "titulo": "Modificar servicio de comedor"
        }
    )

@admin_required
def comedor_desactivar(
    request,
    id_servicio_comedor
):

    servicio = get_object_or_404(
        ServicioComedor,
        id_servicio_comedor=id_servicio_comedor
    )

    if request.method == "POST":

        servicio.estado = False
        servicio.save()

        messages.success(
            request,
            "El servicio de comedor fue desactivado correctamente."
        )

    return redirect(
        "comedor_lista"
    )

#Contratar Comedor
@admin_required
def comedor_contratacion_lista(request):

    contrataciones = (
        ContratacionComedor.objects
        .select_related(
            "alumno",
            "servicio",
            "alumno__curso",
            "alumno__curso__nivel",
        )
        .order_by(
            "-anio",
            "-mes",
            "alumno__apellido",
        )
    )

    return render(
        request,
        "services/comedor/contrataciones/lista.html",
        {
            "contrataciones": contrataciones
        }
    )

@admin_required
def comedor_contratacion_crear(request):

    if request.method == "POST":

        form = ContratacionComedorForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "La contratación de comedor fue registrada correctamente."
            )

            return redirect(
                "comedor_contratacion_lista"
            )

    else:

        form = ContratacionComedorForm()

    return render(
        request,
        "services/comedor/contrataciones/formulario.html",
        {
            "form": form,
            "titulo": "Nueva contratación de comedor"
        }
    )

@admin_required
def comedor_contratacion_editar(
    request,
    id_contratacion
):

    contratacion = get_object_or_404(
        ContratacionComedor,
        id_contratacion_comedor=id_contratacion
    )

    if request.method == "POST":

        form = ContratacionComedorForm(
            request.POST,
            instance=contratacion
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "La contratación de comedor fue modificada correctamente."
            )

            return redirect(
                "comedor_contratacion_lista"
            )

    else:

        form = ContratacionComedorForm(
            instance=contratacion
        )

    return render(
        request,
        "services/comedor/contrataciones/formulario.html",
        {
            "form": form,
            "titulo": "Modificar contratación de comedor"
        }
    )

@admin_required
def comedor_contratacion_desactivar(
    request,
    id_contratacion
):

    contratacion = get_object_or_404(
        ContratacionComedor,
        id_contratacion_comedor=id_contratacion
    )

    if request.method == "POST":

        contratacion.estado = False
        contratacion.save()

        messages.success(
            request,
            "La contratación de comedor fue cancelada correctamente."
        )

    return redirect(
        "comedor_contratacion_lista"
    )