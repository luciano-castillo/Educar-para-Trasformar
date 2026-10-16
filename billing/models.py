from django.db import models
from decimal import Decimal

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
    
class Factura(models.Model):

    ESTADOS = [
        ("PENDIENTE", "Pendiente"),
        ("PARCIAL", "Pago parcial"),
        ("PAGADA", "Pagada"),
        ("VENCIDA", "Vencida"),
        ("ANULADA", "Anulada"),
    ]

    id_factura = models.BigAutoField(
        primary_key=True
    )

    alumno = models.ForeignKey(
        "academic.Alumno",
        on_delete=models.PROTECT,
        related_name="facturas"
    )

    mes = models.PositiveSmallIntegerField(
        choices=CuotaMensual.MESES
    )

    anio = models.PositiveSmallIntegerField()

    fecha_emision = models.DateField(
        auto_now_add=True
    )

    fecha_vencimiento = models.DateField()

    estado = models.CharField(
        max_length=10,
        choices=ESTADOS,
        default="PENDIENTE"
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "alumno",
                    "mes",
                    "anio",
                ],
                name="factura_alumno_periodo_unico"
            )
        ]

        ordering = [
            "-anio",
            "-mes",
            "alumno__apellido",
        ]

    @property
    def total(self):

        return sum(
            (
                detalle.importe
                for detalle in self.detalles.all()
            ),
            Decimal("0.00")
        )

    def __str__(self):

        return (
            f"Factura {self.id_factura} - "
            f"{self.alumno.apellido}, "
            f"{self.alumno.nombre} - "
            f"{self.get_mes_display()} "
            f"{self.anio}"
        )

class DetalleFactura(models.Model):

    TIPOS_CONCEPTO = [
        ("CUOTA", "Cuota mensual"),
        ("DEPORTE", "Deporte"),
        ("TRANSPORTE", "Transporte"),
        ("COMEDOR", "Comedor"),
    ]

    id_detalle = models.BigAutoField(
        primary_key=True
    )

    factura = models.ForeignKey(
        Factura,
        on_delete=models.CASCADE,
        related_name="detalles"
    )

    tipo_concepto = models.CharField(
        max_length=20,
        choices=TIPOS_CONCEPTO
    )

    descripcion = models.CharField(
        max_length=200
    )

    importe = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    cuota_mensual = models.ForeignKey(
        CuotaMensual,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="detalles_factura"
    )

    grupo_deportivo = models.ForeignKey(
        "sports.GrupoDeportivo",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="detalles_factura"
    )

    ruta_transporte = models.ForeignKey(
        "services.RutaTransporte",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="detalles_factura"
    )

    servicio_comedor = models.ForeignKey(
        "services.ServicioComedor",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="detalles_factura"
    )

    class Meta:

        constraints = [

            models.CheckConstraint(
                condition=models.Q(
                    importe__gt=0
                ),
                name="detalle_factura_importe_positivo"
            ),
        ]

    def __str__(self):

        return (
            f"{self.descripcion} - "
            f"${self.importe}"
        )