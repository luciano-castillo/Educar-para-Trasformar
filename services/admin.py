from django.contrib import admin
from .models import RutaTransporte, ContratacionTransporte, ServicioComedor, ContratacionComedor


@admin.register(RutaTransporte)
class RutaTransporteAdmin(admin.ModelAdmin):

    list_display = (
        "id_ruta",
        "nombre",
        "valor_mensual",
        "estado",
    )

    search_fields = (
        "nombre",
    )

    list_filter = (
        "estado",
    )

@admin.register(ContratacionTransporte)
class ContratacionTransporteAdmin(admin.ModelAdmin):

    list_display = (
        "id_contratacion",
        "alumno",
        "ruta",
        "mes",
        "anio",
        "estado",
    )

    list_filter = (
        "anio",
        "mes",
        "estado",
        "ruta",
    )

    search_fields = (
        "alumno__nombre",
        "alumno__apellido",
        "alumno__dni",
        "alumno__legajo",
    )

@admin.register(ServicioComedor)
class ServicioComedorAdmin(admin.ModelAdmin):

    list_display = (
        "id_servicio_comedor",
        "nombre",
        "valor_mensual",
        "estado",
    )

    search_fields = (
        "nombre",
    )

    list_filter = (
        "estado",
    )

@admin.register(ContratacionComedor)
class ContratacionComedorAdmin(admin.ModelAdmin):

    list_display = (
        "id_contratacion_comedor",
        "alumno",
        "servicio",
        "mes",
        "anio",
        "estado",
    )

    list_filter = (
        "anio",
        "mes",
        "estado",
    )

    search_fields = (
        "alumno__nombre",
        "alumno__apellido",
        "alumno__dni",
        "alumno__legajo",
    )