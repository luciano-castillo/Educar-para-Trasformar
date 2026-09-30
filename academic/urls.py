from django.urls import path
from . import views


urlpatterns = [
    #Alumnos
    path(
        "alumnos/",
        views.alumno_lista,
        name="alumno_lista"
    ),

    path(
        "alumnos/nuevo/",
        views.alumno_crear,
        name="alumno_crear"
    ),

    path(
        "alumnos/<int:id_alumno>/editar/",
        views.alumno_editar,
        name="alumno_editar"
    ),

    path(
        "alumnos/<int:id_alumno>/desactivar/",
        views.alumno_desactivar,
        name="alumno_desactivar"
    ),
    
    path(
        "alumno/mis-datos/",
        views.alumno_mis_datos,
        name="alumno_mis_datos"
    ),

    path(
        "alumno/mis-datos/editar/",
        views.alumno_editar_mis_datos,
        name="alumno_editar_mis_datos"
    ),
    #profesores
    
    path(
        "profesores/",
        views.profesor_lista,
        name="profesor_lista"
    ),

    path(
        "profesores/nuevo/",
        views.profesor_crear,
        name="profesor_crear"
    ),

    path(
        "profesores/<int:id_profesor>/editar/",
        views.profesor_editar,
        name="profesor_editar"
    ),

    path(
        "profesores/<int:id_profesor>/desactivar/",
        views.profesor_desactivar,
        name="profesor_desactivar"
    ),
    
    path(
        "profesor/mis-datos/",
        views.profesor_mis_datos,
        name="profesor_mis_datos"
    ),

    path(
        "profesor/mis-datos/editar/",
        views.profesor_editar_mis_datos,
        name="profesor_editar_mis_datos"
    ),
    #Materias
    path(
        "materias/",
        views.materia_lista,
        name="materia_lista"
    ),

    path(
        "materias/nueva/",
        views.materia_crear,
        name="materia_crear"
    ),

    path(
        "materias/<int:id_materia>/editar/",
        views.materia_editar,
        name="materia_editar"
    ),

    path(
        "materias/<int:id_materia>/desactivar/",
        views.materia_desactivar,
        name="materia_desactivar"
    ),
    #Horarios
    path(
        "horarios/",
        views.horario_lista,
        name="horario_lista"
    ),

    path(
        "horarios/nuevo/",
        views.horario_crear,
        name="horario_crear"
    ),

    path(
        "horarios/<int:id_horario>/editar/",
        views.horario_editar,
        name="horario_editar"
    ),

    path(
        "horarios/<int:id_horario>/eliminar/",
        views.horario_eliminar,
        name="horario_eliminar"
    ),
    path(
        "dictados/",
        views.dictado_lista,
        name="dictado_lista"
    ),

    path(
        "dictados/nuevo/",
        views.dictado_crear,
        name="dictado_crear"
    ),

    path(
        "dictados/<int:id_dictado>/editar/",
        views.dictado_editar,
        name="dictado_editar"
    ), 
    
    # Niveles educativos

    path(
        "niveles/",
        views.nivel_lista,
        name="nivel_lista"
    ),

    path(
        "niveles/nuevo/",
        views.nivel_crear,
        name="nivel_crear"
    ),

    path(
        "niveles/<int:id_nivel>/editar/",
        views.nivel_editar,
        name="nivel_editar"
    ),

    path(
        "niveles/<int:id_nivel>/desactivar/",
        views.nivel_desactivar,
        name="nivel_desactivar"
    ),


    # Cursos

    path(
        "cursos/",
        views.curso_lista,
        name="curso_lista"
    ),

    path(
        "cursos/nuevo/",
        views.curso_crear,
        name="curso_crear"
    ),

    path(
        "cursos/<int:id_curso>/editar/",
        views.curso_editar,
        name="curso_editar"
    ),

    path(
        "cursos/<int:id_curso>/desactivar/",
        views.curso_desactivar,
        name="curso_desactivar"
    ),

]
