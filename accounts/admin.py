from django.contrib import admin
from .models import PerfilUsuario


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):

    list_display = (
        "id_perfil",
        "usuario",
        "rol",
    )

    search_fields = (
        "usuario__username",
        "usuario__email",
    )

    list_filter = (
        "rol",
    )
