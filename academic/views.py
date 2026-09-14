from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Alumno
from .forms import AlumnoForm

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