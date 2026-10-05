from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)

from django.contrib import messages

from .models import Deporte, GrupoDeportivo, InscripcionDeporte
from .forms import DeporteForm, GrupoDeportivoForm, InscripcionDeporteForm

from accounts.decorators import admin_required

@admin_required
def deporte_lista(request):

    deportes = (
        Deporte.objects
        .all()
        .order_by("nombre")
    )

    return render(
        request,
        "sports/deportes/lista.html",
        {
            "deportes": deportes
        }
    )

@admin_required
def deporte_crear(request):

    if request.method == "POST":

        form = DeporteForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "El deporte fue registrado correctamente."
            )

            return redirect(
                "deporte_lista"
            )

    else:

        form = DeporteForm()

    return render(
        request,
        "sports/deportes/formulario.html",
        {
            "form": form,
            "titulo": "Nuevo deporte"
        }
    )

@admin_required
def deporte_editar(
    request,
    id_deporte
):

    deporte = get_object_or_404(
        Deporte,
        id_deporte=id_deporte
    )

    if request.method == "POST":

        form = DeporteForm(
            request.POST,
            instance=deporte
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "El deporte fue modificado correctamente."
            )

            return redirect(
                "deporte_lista"
            )

    else:

        form = DeporteForm(
            instance=deporte
        )

    return render(
        request,
        "sports/deportes/formulario.html",
        {
            "form": form,
            "titulo": "Modificar deporte"
        }
    )

@admin_required
def deporte_desactivar(
    request,
    id_deporte
):

    deporte = get_object_or_404(
        Deporte,
        id_deporte=id_deporte
    )

    if request.method == "POST":

        deporte.estado = False
        deporte.save()

        messages.success(
            request,
            "El deporte fue desactivado correctamente."
        )

    return redirect(
        "deporte_lista"
    )

@admin_required
def grupo_lista(request):

    grupos = (
        GrupoDeportivo.objects
        .select_related(
            "deporte",
            "nivel",
            "profesor",
            "horario"
        )
        .order_by(
            "deporte__nombre",
            "nivel__nombre"
        )
    )

    return render(
        request,
        "sports/grupos/lista.html",
        {
            "grupos": grupos
        }
    )

@admin_required
def grupo_crear(request):

    if request.method == "POST":

        form = GrupoDeportivoForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "El grupo deportivo fue registrado correctamente."
            )

            return redirect(
                "grupo_lista"
            )

    else:

        form = GrupoDeportivoForm()

    return render(
        request,
        "sports/grupos/formulario.html",
        {
            "form": form,
            "titulo": "Nuevo grupo deportivo"
        }
    )

@admin_required
def grupo_editar(
    request,
    id_grupo
):

    grupo = get_object_or_404(
        GrupoDeportivo,
        id_grupo=id_grupo
    )

    if request.method == "POST":

        form = GrupoDeportivoForm(
            request.POST,
            instance=grupo
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "El grupo deportivo fue modificado correctamente."
            )

            return redirect(
                "grupo_lista"
            )

    else:

        form = GrupoDeportivoForm(
            instance=grupo
        )

    return render(
        request,
        "sports/grupos/formulario.html",
        {
            "form": form,
            "titulo": "Modificar grupo deportivo"
        }
    )

@admin_required
def grupo_desactivar(request, id_grupo):

    grupo = get_object_or_404(
        GrupoDeportivo,
        id_grupo=id_grupo
    )

    if request.method == "POST":

        grupo.estado = False
        grupo.save()

        messages.success(
            request,
            "El grupo deportivo fue desactivado correctamente."
        )

    return redirect("grupo_lista")

#Inscripciones a Deportes
@admin_required
def inscripcion_lista(request):

    inscripciones = (
        InscripcionDeporte.objects
        .select_related(
            "alumno",
            "grupo",
            "grupo__deporte",
            "grupo__nivel",
            "grupo__profesor",
            "grupo__horario",
        )
        .order_by(
            "alumno__apellido",
            "alumno__nombre",
        )
    )

    return render(
        request,
        "sports/inscripciones/lista.html",
        {
            "inscripciones": inscripciones
        }
    )

@admin_required
def inscripcion_crear(request):

    if request.method == "POST":

        form = InscripcionDeporteForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "La inscripción deportiva fue registrada correctamente."
            )

            return redirect(
                "inscripcion_lista"
            )

    else:

        form = InscripcionDeporteForm()

    return render(
        request,
        "sports/inscripciones/formulario.html",
        {
            "form": form,
            "titulo": "Nueva inscripción deportiva"
        }
    )

@admin_required
def inscripcion_desactivar(
    request,
    id_inscripcion
):

    inscripcion = get_object_or_404(
        InscripcionDeporte,
        id_inscripcion=id_inscripcion
    )

    if request.method == "POST":

        inscripcion.estado = False
        inscripcion.save()

        messages.success(
            request,
            "La inscripción deportiva fue finalizada correctamente."
        )

    return redirect(
        "inscripcion_lista"
    )