from django.contrib import admin

from .models import CuotaMensual


@admin.register(CuotaMensual)
class CuotaMensualAdmin(admin.ModelAdmin):

    list_display = (
        "mes",
        "anio",
        "valor",
        "fecha_vencimiento",
        "estado",
    )

    list_filter = (
        "anio",
        "mes",
        "estado",
    )

    ordering = (
        "-anio",
        "-mes",
    )
