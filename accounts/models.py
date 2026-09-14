from django.db import models
from django.contrib.auth.models import User


class PerfilUsuario(models.Model):

    class Rol(models.TextChoices):
        ADMIN = "ADMIN", "Administrador"
        DOCENTE = "DOCENTE", "Docente"
        ALUMNO = "ALUMNO", "Alumno"
        TUTOR = "TUTOR", "Padre / Tutor"

    id_perfil = models.BigAutoField(
        primary_key=True
    )

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="perfil"
    )

    rol = models.CharField(
        max_length=10,
        choices=Rol.choices
    )

    def __str__(self):
        return f"{self.usuario.username} - {self.get_rol_display()}"