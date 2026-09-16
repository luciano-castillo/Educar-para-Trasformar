from django.contrib import admin
from .models import NivelEducativo, Curso, Alumno, Profesor, Materia, Horario, DictadoMateria


@admin.register(NivelEducativo)
class NivelEducativoAdmin(admin.ModelAdmin):
    list_display = ("id_nivel", "nombre", "estado")
    search_fields = ("nombre",)
    list_filter = ("estado",)

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = (
        "id_curso",
        "nombre",
        "division",
        "turno",
        "nivel",
        "estado",
    )

    search_fields = (
        "nombre",
        "division",
    )

    list_filter = (
        "nivel",
        "turno",
        "estado",
    )

@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = (
        "id_alumno",
        "legajo",
        "dni",
        "apellido",
        "nombre",
        "usuario",
        "curso",
        "estado",
    )

    search_fields = (
        "legajo",
        "dni",
        "nombre",
        "apellido",
        "correo",
    )

    list_filter = (
        "estado",
        "curso",
        "curso__nivel",
    )

    ordering = (
        "apellido",
        "nombre",
    )

@admin.register(Profesor)
class ProfesorAdmin(admin.ModelAdmin):

    list_display = (
        "id_profesor",
        "legajo",
        "dni",
        "apellido",
        "nombre",
        "especialidad",
        "usuario",
        "estado",
    )

    search_fields = (
        "legajo",
        "dni",
        "nombre",
        "apellido",
        "especialidad",
        "correo",
        "usuario__username",
    )

    list_filter = (
        "estado",
        "especialidad",
    )

    ordering = (
        "apellido",
        "nombre",
    )

@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display = (
        "id_materia",
        "nombre",
        "estado",
    )

    search_fields = (
        "nombre",
    )

    list_filter = (
        "estado",
    )

@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = (
        "id_horario",
        "dia_semana",
        "hora_inicio",
        "hora_fin",
    )

    list_filter = (
        "dia_semana",
    )

@admin.register(DictadoMateria)
class DictadoMateriaAdmin(admin.ModelAdmin):
    list_display = (
        "id_dictado",
        "materia",
        "profesor",
        "curso",
        "horario",
    )

    search_fields = (
        "materia__nombre",
        "profesor__nombre",
        "profesor__apellido",
        "curso__nombre",
    )

    list_filter = (
        "materia",
        "profesor",
        "curso",
    )