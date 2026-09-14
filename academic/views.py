from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from accounts.decorators import admin_required, alumno_required

from .models import Alumno
from .forms import AlumnoForm, AlumnoDatosPersonalesForm

@admin_required
def alumno_lista(request):
    alumnos = Alumno.objects.select_related(
        "curso",
        "curso__nivel"
    ).all().order_by("apellido", "nombre")

    return render(
        request,
        "academic/alumnos/lista.html",
        {"alumnos": alumnos}
    )
    
@admin_required
def alumno_crear(request):

    if request.method == "POST":

        form = AlumnoForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Alumno registrado correctamente."
            )

            return redirect("alumno_lista")

    else:
        form = AlumnoForm()

    return render(
        request,
        "academic/alumnos/formulario.html",
        {
            "form": form,
            "titulo": "Registrar alumno"
        }
    )

@admin_required
def alumno_editar(request, id_alumno):

    alumno = get_object_or_404(
        Alumno,
        id_alumno=id_alumno
    )

    if request.method == "POST":

        form = AlumnoForm(
            request.POST,
            instance=alumno
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Alumno modificado correctamente."
            )

            return redirect("alumno_lista")

    else:
        form = AlumnoForm(instance=alumno)

    return render(
        request,
        "academic/alumnos/formulario.html",
        {
            "form": form,
            "titulo": "Modificar alumno"
        }
    )

@admin_required
def alumno_desactivar(request, id_alumno):

    alumno = get_object_or_404(
        Alumno,
        id_alumno=id_alumno
    )

    if request.method == "POST":

        alumno.estado = False
        alumno.save()

        messages.success(
            request,
            "Alumno desactivado correctamente."
        )

    return redirect("alumno_lista")

@alumno_required
def alumno_mis_datos(request):

    try:
        alumno = request.user.alumno

    except Alumno.DoesNotExist:

        messages.error(
            request,
            "Su cuenta no está asociada a un alumno."
        )

        return redirect("inicio_por_rol")

    return render(
        request,
        "academic/alumnos/mis_datos.html",
        {
            "alumno": alumno
        }
    )
    
@alumno_required
def alumno_editar_mis_datos(request):

    try:
        alumno = request.user.alumno

    except Alumno.DoesNotExist:

        messages.error(
            request,
            "Su cuenta no está asociada a un alumno."
        )

        return redirect("inicio_por_rol")

    if request.method == "POST":

        form = AlumnoDatosPersonalesForm(
            request.POST,
            instance=alumno
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Sus datos fueron actualizados correctamente."
            )

            return redirect("alumno_mis_datos")

    else:

        form = AlumnoDatosPersonalesForm(
            instance=alumno
        )

    return render(
        request,
        "academic/alumnos/editar_mis_datos.html",
        {
            "form": form,
            "alumno": alumno
        }
    )