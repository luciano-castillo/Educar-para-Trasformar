from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models.deletion import ProtectedError

from accounts.decorators import admin_required, alumno_required, docente_required

from .models import Alumno, Profesor, Materia, Horario, DictadoMateria, NivelEducativo, Curso
from .forms import (
    AlumnoForm, 
    AlumnoDatosPersonalesForm, 
    ProfesorForm, 
    ProfesorDatosPersonalesForm, 
    MateriaForm, 
    HorarioForm,
    DictadoMateriaForm,
    CursoForm,
    NivelEducativoForm,
    )

#Alumnos
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

#Profesores
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

#Materias
@admin_required
def materia_lista(request):

    materias = Materia.objects.all().order_by("nombre")

    return render(
        request,
        "academic/materias/lista.html",
        {
            "materias": materias
        }
    )

@admin_required
def materia_crear(request):

    if request.method == "POST":

        form = MateriaForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "La materia fue registrada correctamente."
            )

            return redirect("materia_lista")

    else:

        form = MateriaForm()

    return render(
        request,
        "academic/materias/formulario.html",
        {
            "form": form,
            "titulo": "Nueva materia"
        }
    )
    
@admin_required
def materia_editar(request, id_materia):

    materia = get_object_or_404(
        Materia,
        id_materia=id_materia
    )

    if request.method == "POST":

        form = MateriaForm(
            request.POST,
            instance=materia
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "La materia fue modificada correctamente."
            )

            return redirect("materia_lista")

    else:

        form = MateriaForm(
            instance=materia
        )

    return render(
        request,
        "academic/materias/formulario.html",
        {
            "form": form,
            "titulo": "Modificar materia"
        }
    )

@admin_required
def materia_desactivar(request, id_materia):

    materia = get_object_or_404(
        Materia,
        id_materia=id_materia
    )

    if request.method == "POST":

        materia.estado = False
        materia.save()

        messages.success(
            request,
            "La materia fue desactivada correctamente."
        )

    return redirect("materia_lista")

#Horarios
@admin_required
def horario_lista(request):

    horarios = Horario.objects.all().order_by(
        "dia_semana",
        "hora_inicio"
    )

    return render(
        request,
        "academic/horarios/lista.html",
        {
            "horarios": horarios
        }
    )

@admin_required
def horario_crear(request):

    if request.method == "POST":

        form = HorarioForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "El horario fue registrado correctamente."
            )

            return redirect("horario_lista")

    else:

        form = HorarioForm()

    return render(
        request,
        "academic/horarios/formulario.html",
        {
            "form": form,
            "titulo": "Nuevo horario"
        }
    )

@admin_required
def horario_editar(request, id_horario):

    horario = get_object_or_404(
        Horario,
        id_horario=id_horario
    )

    if request.method == "POST":

        form = HorarioForm(
            request.POST,
            instance=horario
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "El horario fue modificado correctamente."
            )

            return redirect("horario_lista")

    else:

        form = HorarioForm(
            instance=horario
        )

    return render(
        request,
        "academic/horarios/formulario.html",
        {
            "form": form,
            "titulo": "Modificar horario"
        }
    )

@admin_required
def horario_eliminar(request, id_horario):

    horario = get_object_or_404(
        Horario,
        id_horario=id_horario
    )

    if request.method == "POST":

        try:

            horario.delete()

            messages.success(
                request,
                "El horario fue eliminado correctamente."
            )

        except ProtectedError:

            messages.error(
                request,
                "No se puede eliminar el horario porque está asignado a una materia."
            )

    return redirect("horario_lista")

#DictadoMaterias
@admin_required
def dictado_lista(request):

    dictados = (
        DictadoMateria.objects
        .select_related(
            "materia",
            "profesor",
            "curso",
            "curso__nivel",
            "horario"
        )
        .order_by(
            "curso__nivel__nombre",
            "curso__nombre",
            "materia__nombre"
        )
    )

    return render(
        request,
        "academic/dictados/lista.html",
        {
            "dictados": dictados
        }
    )

@admin_required
def dictado_crear(request):

    if request.method == "POST":

        form = DictadoMateriaForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "La asignación fue registrada correctamente."
            )

            return redirect("dictado_lista")

    else:

        form = DictadoMateriaForm()

    return render(
        request,
        "academic/dictados/formulario.html",
        {
            "form": form,
            "titulo": "Nueva asignación"
        }
    )

@admin_required
def dictado_editar(request, id_dictado):

    dictado = get_object_or_404(
        DictadoMateria,
        id_dictado=id_dictado
    )

    if request.method == "POST":

        form = DictadoMateriaForm(
            request.POST,
            instance=dictado
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "La asignación fue modificada correctamente."
            )

            return redirect("dictado_lista")

    else:

        form = DictadoMateriaForm(
            instance=dictado
        )

    return render(
        request,
        "academic/dictados/formulario.html",
        {
            "form": form,
            "titulo": "Modificar asignación"
        }
    )

#Nivel Educativo
@admin_required
def nivel_lista(request):

    niveles = NivelEducativo.objects.all().order_by("nombre")

    return render(
        request,
        "academic/niveles/lista.html",
        {
            "niveles": niveles
        }
    )

@admin_required
def nivel_crear(request):

    if request.method == "POST":

        form = NivelEducativoForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "El nivel educativo fue registrado correctamente."
            )

            return redirect("nivel_lista")

    else:

        form = NivelEducativoForm()

    return render(
        request,
        "academic/niveles/formulario.html",
        {
            "form": form,
            "titulo": "Nuevo nivel educativo"
        }
    )

@admin_required
def nivel_editar(request, id_nivel):

    nivel = get_object_or_404(
        NivelEducativo,
        id_nivel=id_nivel
    )

    if request.method == "POST":

        form = NivelEducativoForm(
            request.POST,
            instance=nivel
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "El nivel educativo fue modificado correctamente."
            )

            return redirect("nivel_lista")

    else:

        form = NivelEducativoForm(
            instance=nivel
        )

    return render(
        request,
        "academic/niveles/formulario.html",
        {
            "form": form,
            "titulo": "Modificar nivel educativo"
        }
    )

@admin_required
def nivel_desactivar(request, id_nivel):

    nivel = get_object_or_404(
        NivelEducativo,
        id_nivel=id_nivel
    )

    if request.method == "POST":

        nivel.estado = False
        nivel.save()

        messages.success(
            request,
            "El nivel educativo fue desactivado correctamente."
        )

    return redirect("nivel_lista")

#Curso
@admin_required
def curso_lista(request):

    cursos = (
        Curso.objects
        .select_related("nivel")
        .all()
        .order_by(
            "nivel__nombre",
            "nombre",
            "division"
        )
    )

    return render(
        request,
        "academic/cursos/lista.html",
        {
            "cursos": cursos
        }
    )

@admin_required
def curso_crear(request):

    if request.method == "POST":

        form = CursoForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "El curso fue registrado correctamente."
            )

            return redirect("curso_lista")

    else:

        form = CursoForm()

    return render(
        request,
        "academic/cursos/formulario.html",
        {
            "form": form,
            "titulo": "Nuevo curso"
        }
    )

@admin_required
def curso_editar(request, id_curso):

    curso = get_object_or_404(
        Curso,
        id_curso=id_curso
    )

    if request.method == "POST":

        form = CursoForm(
            request.POST,
            instance=curso
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "El curso fue modificado correctamente."
            )

            return redirect("curso_lista")

    else:

        form = CursoForm(
            instance=curso
        )

    return render(
        request,
        "academic/cursos/formulario.html",
        {
            "form": form,
            "titulo": "Modificar curso"
        }
    )

@admin_required
def curso_desactivar(request, id_curso):

    curso = get_object_or_404(
        Curso,
        id_curso=id_curso
    )

    if request.method == "POST":

        curso.estado = False
        curso.save()

        messages.success(
            request,
            "El curso fue desactivado correctamente."
        )

    return redirect("curso_lista")
