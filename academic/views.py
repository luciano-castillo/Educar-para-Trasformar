from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from accounts.decorators import admin_required, alumno_required, docente_required

from .models import Alumno, Profesor
from .forms import AlumnoForm, AlumnoDatosPersonalesForm, ProfesorForm, ProfesorDatosPersonalesForm

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

@admin_required
def profesor_lista(request):

    profesores = Profesor.objects.all().order_by(
        "apellido",
        "nombre"
    )

    return render(
        request,
        "academic/profesores/lista.html",
        {
            "profesores": profesores
        }
    )

@admin_required
def profesor_crear(request):

    if request.method == "POST":

        form = ProfesorForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Profesor registrado correctamente."
            )

            return redirect("profesor_lista")

    else:

        form = ProfesorForm()

    return render(
        request,
        "academic/profesores/formulario.html",
        {
            "form": form,
            "titulo": "Registrar profesor"
        }
    )

@admin_required
def profesor_editar(request, id_profesor):

    profesor = get_object_or_404(
        Profesor,
        id_profesor=id_profesor
    )

    if request.method == "POST":

        form = ProfesorForm(
            request.POST,
            instance=profesor
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Profesor modificado correctamente."
            )

            return redirect("profesor_lista")

    else:

        form = ProfesorForm(
            instance=profesor
        )

    return render(
        request,
        "academic/profesores/formulario.html",
        {
            "form": form,
            "titulo": "Modificar profesor"
        }
    )
    
@admin_required
def profesor_desactivar(request, id_profesor):

    profesor = get_object_or_404(
        Profesor,
        id_profesor=id_profesor
    )

    if request.method == "POST":

        profesor.estado = False
        profesor.save()

        messages.success(
            request,
            "Profesor desactivado correctamente."
        )

    return redirect("profesor_lista")

@docente_required
def profesor_mis_datos(request):

    try:
        profesor = request.user.profesor

    except Profesor.DoesNotExist:

        messages.error(
            request,
            "Su cuenta no está asociada a un profesor."
        )

        return redirect("inicio_por_rol")

    dictados = profesor.dictados.select_related(
        "materia",
        "curso",
        "curso__nivel",
        "horario"
    ).filter(
        materia__estado=True,
        curso__estado=True
    ).order_by(
        "materia__nombre",
        "curso__nombre"
    )

    return render(
        request,
        "academic/profesores/mis_datos.html",
        {
            "profesor": profesor,
            "dictados": dictados,
        }
    )

@docente_required
def profesor_editar_mis_datos(request):

    try:
        profesor = request.user.profesor

    except Profesor.DoesNotExist:

        messages.error(
            request,
            "Su cuenta no está asociada a un profesor."
        )

        return redirect("inicio_por_rol")

    if request.method == "POST":

        form = ProfesorDatosPersonalesForm(
            request.POST,
            instance=profesor
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Sus datos fueron actualizados correctamente."
            )

            return redirect("profesor_mis_datos")

    else:

        form = ProfesorDatosPersonalesForm(
            instance=profesor
        )

    return render(
        request,
        "academic/profesores/editar_mis_datos.html",
        {
            "form": form,
            "profesor": profesor
        }
    )