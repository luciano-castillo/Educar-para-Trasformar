from django.db import models


class CuotaMensual(models.Model):

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

    id_cuota = models.BigAutoField(
        primary_key=True
    )

    mes = models.PositiveSmallIntegerField(
        choices=MESES
    )

    anio = models.PositiveSmallIntegerField()

    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    fecha_vencimiento = models.DateField()

    estado = models.BooleanField(
        default=True
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "mes",
                    "anio",
                ],
                name="cuota_periodo_unico"
            )
        ]

        ordering = [
            "-anio",
            "-mes",
        ]

    def __str__(self):

        return (
            f"{self.get_mes_display()} "
            f"{self.anio} - "
            f"${self.valor}"
        )
