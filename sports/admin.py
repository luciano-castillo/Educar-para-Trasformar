from django.contrib import admin
from .models import Deporte, GrupoDeportivo, InscripcionDeporte


@admin.register(Deporte)
class DeporteAdmin(admin.ModelAdmin):

    list_display = (
        "id_deporte",
        "nombre",
        "estado",
    )

    search_fields = (
        "nombre",
    )

    list_filter = (
        "estado",
    )

@admin.register(GrupoDeportivo)
class GrupoDeportivoAdmin(admin.ModelAdmin):

    list_display = (
        "id_grupo",
        "deporte",
        "nivel",
        "profesor",
        "horario",
    )

    list_filter = (
        "deporte",
        "nivel",
    )

@admin.register(InscripcionDeporte)
class InscripcionDeporteAdmin(admin.ModelAdmin):

    list_display = (
        "id_inscripcion",
        "alumno",
        "grupo",
        "fecha_inscripcion",
        "estado",
    )

    list_filter = (
        "estado",
        "grupo__deporte",
    )

    search_fields = (
        "alumno__nombre",
        "alumno__apellido",
        "alumno__dni",
        "alumno__legajo",
    )