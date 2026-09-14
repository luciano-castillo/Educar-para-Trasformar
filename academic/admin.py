from django.contrib import admin
from .models import NivelEducativo, Curso, Alumno


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