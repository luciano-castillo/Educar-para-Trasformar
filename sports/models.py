from django.db import models
from academic.models import (
    NivelEducativo,
    Profesor,
    Horario,
    Alumno,
)

class Deporte(models.Model):

    id_deporte = models.BigAutoField(
        primary_key=True
    )

    nombre = models.CharField(
        max_length=100,
        unique=True
    )

    descripcion = models.CharField(
        max_length=250,
        blank=True
    )

    estado = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.nombre



class GrupoDeportivo(models.Model):

    id_grupo = models.BigAutoField(
        primary_key=True
    )

    deporte = models.ForeignKey(
        Deporte,
        on_delete=models.PROTECT,
        related_name="grupos"
    )

    nivel = models.ForeignKey(
        NivelEducativo,
        on_delete=models.PROTECT,
        related_name="grupos_deportivos"
    )

    profesor = models.ForeignKey(
        Profesor,
        on_delete=models.PROTECT,
        related_name="grupos_deportivos"
    )

    horario = models.ForeignKey(
        Horario,
        on_delete=models.PROTECT,
        related_name="grupos_deportivos"
    )

    estado = models.BooleanField(
        default=True
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "deporte",
                    "nivel",
                    "profesor",
                    "horario",
                ],
                name="grupo_deportivo_unico"
            )
        ]

    def __str__(self):

        return (
            f"{self.deporte.nombre} - "
            f"{self.nivel.nombre} - "
            f"{self.profesor.apellido}"
        )

class InscripcionDeporte(models.Model):

    id_inscripcion = models.BigAutoField(
        primary_key=True
    )

    alumno = models.ForeignKey(
        Alumno,
        on_delete=models.PROTECT,
        related_name="inscripciones_deportivas"
    )

    grupo = models.ForeignKey(
        GrupoDeportivo,
        on_delete=models.PROTECT,
        related_name="inscripciones"
    )

    fecha_inscripcion = models.DateField(
        auto_now_add=True
    )

    estado = models.BooleanField(
        default=True
    )

    def __str__(self):
        return (
            f"{self.alumno.apellido}, "
            f"{self.alumno.nombre} - "
            f"{self.grupo.deporte.nombre}"
        )