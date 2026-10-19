from django.db import models
from decimal import Decimal
from django.conf import settings
from django.db.models import Sum
from django.core.validators import FileExtensionValidator

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
    
    @property
    def total_pagado(self):

        resultado = (
            self.pagos
            .filter(
                estado="VALIDADO"
            )
            .aggregate(
                total=Sum(
                    "detalles_pago__importe_aplicado"
                )
            )
        )

        return (
            resultado["total"]
            or Decimal("0.00")
        )


    @property
    def saldo(self):

        saldo = (
            self.total
            - self.total_pagado
        )

        if saldo < 0:
            return Decimal("0.00")

        return saldo


    def actualizar_estado_pago(self):

        if self.estado == "ANULADA":
            return

        if self.total_pagado <= 0:

            nuevo_estado = "PENDIENTE"

        elif self.total_pagado < self.total:

            nuevo_estado = "PARCIAL"

        else:

            nuevo_estado = "PAGADA"

        if self.estado != nuevo_estado:

            self.estado = nuevo_estado

            self.save(
                update_fields=[
                    "estado"
                ]
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
    
    @property
    def total_pagado(self):

        resultado = (
            self.aplicaciones_pago
            .filter(
                pago__estado="VALIDADO"
            )
            .aggregate(
                total=Sum(
                    "importe_aplicado"
                )
            )
        )

        return (
            resultado["total"]
            or Decimal("0.00")
        )


    @property
    def saldo_pendiente(self):

        saldo = (
            self.importe
            - self.total_pagado
        )

        if saldo < 0:
            return Decimal("0.00")

        return saldo


    @property
    def saldo_disponible_pago(self):

        utilizado = (
            self.aplicaciones_pago
            .exclude(
                pago__estado="RECHAZADO"
            )
            .aggregate(
                total=Sum(
                    "importe_aplicado"
                )
            )["total"]
            or Decimal("0.00")
        )

        disponible = (
            self.importe
            - utilizado
        )

        if disponible < 0:
            return Decimal("0.00")

        return disponible

    def __str__(self):

        return (
            f"{self.descripcion} - "
            f"${self.importe}"
        )

class Pago(models.Model):

    ESTADOS = [
        ("PENDIENTE", "Pendiente"),
        ("VALIDADO", "Validado"),
        ("RECHAZADO", "Rechazado"),
    ]

    id_pago = models.BigAutoField(
        primary_key=True
    )

    factura = models.ForeignKey(
        Factura,
        on_delete=models.PROTECT,
        related_name="pagos"
    )

    fecha_transferencia = models.DateField()

    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    numero_operacion = models.CharField(
        max_length=100,
        blank=True
    )

    estado = models.CharField(
        max_length=10,
        choices=ESTADOS,
        default="PENDIENTE"
    )

    observaciones = models.CharField(
        max_length=250,
        blank=True
    )

    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pagos_registrados"
    )

    fecha_registro = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        ordering = [
            "-fecha_registro"
        ]

        constraints = [

            models.CheckConstraint(
                condition=models.Q(
                    monto__gt=0
                ),
                name="pago_monto_positivo"
            ),
        ]

    def __str__(self):

        return (
            f"Pago {self.id_pago} - "
            f"Factura {self.factura_id} - "
            f"${self.monto}"
        )

class PagoDetalle(models.Model):

    id_pago_detalle = models.BigAutoField(
        primary_key=True
    )

    pago = models.ForeignKey(
        Pago,
        on_delete=models.CASCADE,
        related_name="detalles_pago"
    )

    detalle_factura = models.ForeignKey(
        DetalleFactura,
        on_delete=models.PROTECT,
        related_name="aplicaciones_pago"
    )

    importe_aplicado = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    class Meta:

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "pago",
                    "detalle_factura",
                ],
                name="pago_detalle_unico"
            ),

            models.CheckConstraint(
                condition=models.Q(
                    importe_aplicado__gt=0
                ),
                name="pago_detalle_importe_positivo"
            ),
        ]

    def __str__(self):

        return (
            f"Pago {self.pago_id} - "
            f"{self.detalle_factura.descripcion} - "
            f"${self.importe_aplicado}"
        )

def comprobante_upload_to(
    instance,
    filename
):

    return (
        f"comprobantes/"
        f"factura_{instance.pago.factura_id}/"
        f"pago_{instance.pago_id}/"
        f"{filename}"
    )


class ComprobantePago(models.Model):

    id_comprobante = models.BigAutoField(
        primary_key=True
    )

    pago = models.ForeignKey(
        Pago,
        on_delete=models.CASCADE,
        related_name="comprobantes"
    )

    archivo = models.FileField(
        upload_to=comprobante_upload_to,
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "pdf",
                    "jpg",
                    "jpeg",
                    "png",
                ]
            )
        ]
    )

    fecha_subida = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return (
            f"Comprobante "
            f"{self.id_comprobante} - "
            f"Pago {self.pago_id}"
        )