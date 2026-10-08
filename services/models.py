from django.db import models

from django.db import models
from academic.models import Alumno

class RutaTransporte(models.Model):

    id_ruta = models.BigAutoField(
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

    valor_mensual = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    estado = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.nombre

class ContratacionTransporte(models.Model):

    MESES = [
        (1, "Enero"),
        (2, "Febrero"),
        (3, "Marzo"),
        (4, "Abril"),
        (5, "Mayo"),
        (6, "Junio"),
        (7, "Julio"),
        (8, "Agosto"),
        (9, "Septiembre"),
        (10, "Octubre"),
        (11, "Noviembre"),
        (12, "Diciembre"),
    ]

    id_contratacion = models.BigAutoField(
        primary_key=True
    )

    alumno = models.ForeignKey(
        Alumno,
        on_delete=models.PROTECT,
        related_name="contrataciones_transporte"
    )

    ruta = models.ForeignKey(
        RutaTransporte,
        on_delete=models.PROTECT,
        related_name="contrataciones"
    )

    mes = models.PositiveSmallIntegerField(
        choices=MESES
    )

    anio = models.PositiveSmallIntegerField()

    fecha_registro = models.DateField(
        auto_now_add=True
    )

    estado = models.BooleanField(
        default=True
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "alumno",
                    "mes",
                    "anio",
                ],
                name="transporte_alumno_periodo_unico"
            )
        ]

    def __str__(self):

        return (
            f"{self.alumno.apellido}, "
            f"{self.alumno.nombre} - "
            f"{self.get_mes_display()} "
            f"{self.anio} - "
            f"{self.ruta.nombre}"
        )
    
class ServicioComedor(models.Model):

    id_servicio_comedor = models.BigAutoField(
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

    valor_mensual = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    estado = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.nombre

class ContratacionComedor(models.Model):

    MESES = [
        (1, "Enero"),
        (2, "Febrero"),
        (3, "Marzo"),
        (4, "Abril"),
        (5, "Mayo"),
        (6, "Junio"),
        (7, "Julio"),
        (8, "Agosto"),
        (9, "Septiembre"),
        (10, "Octubre"),
        (11, "Noviembre"),
        (12, "Diciembre"),
    ]

    id_contratacion_comedor = models.BigAutoField(
        primary_key=True
    )

    alumno = models.ForeignKey(
        Alumno,
        on_delete=models.PROTECT,
        related_name="contrataciones_comedor"
    )

    servicio = models.ForeignKey(
        ServicioComedor,
        on_delete=models.PROTECT,
        related_name="contrataciones"
    )

    mes = models.PositiveSmallIntegerField(
        choices=MESES
    )

    anio = models.PositiveSmallIntegerField()

    fecha_registro = models.DateField(
        auto_now_add=True
    )

    estado = models.BooleanField(
        default=True
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "alumno",
                    "mes",
                    "anio",
                ],
                name="comedor_alumno_periodo_unico"
            )
        ]

    def __str__(self):

        return (
            f"{self.alumno.apellido}, "
            f"{self.alumno.nombre} - "
            f"{self.get_mes_display()} "
            f"{self.anio} - "
            f"{self.servicio.nombre}"
        )
