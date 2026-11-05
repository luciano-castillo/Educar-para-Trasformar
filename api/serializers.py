from rest_framework import serializers

from academic.models import Alumno, Curso
from billing.models import (
    ComprobantePago,
    DetalleFactura,
    Factura,
    Pago,
    PagoDetalle,
)


class CursoResumenSerializer(serializers.ModelSerializer):
    nivel = serializers.CharField(source="nivel.nombre", read_only=True)

    class Meta:
        model = Curso

        fields = [
            "id_curso",
            "nombre",
            "division",
            "turno",
            "nivel",
        ]


class AlumnoResumenSerializer(serializers.ModelSerializer):
    curso = CursoResumenSerializer(read_only=True)

    class Meta:
        model = Alumno

        fields = [
            "id_alumno",
            "nombre",
            "apellido",
            "legajo",
            "curso",
        ]


class DetalleFacturaSerializer(serializers.ModelSerializer):
    total_pagado = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    saldo_pendiente = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    saldo_disponible_pago = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = DetalleFactura

        fields = [
            "id_detalle",
            "tipo_concepto",
            "descripcion",
            "importe",
            "total_pagado",
            "saldo_pendiente",
            "saldo_disponible_pago",
        ]


class FacturaSerializer(serializers.ModelSerializer):
    mes_nombre = serializers.CharField(
        source="get_mes_display",
        read_only=True,
    )

    estado_nombre = serializers.CharField(
        source="get_estado_display",
        read_only=True,
    )

    total = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    total_pagado = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    saldo = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    detalles = DetalleFacturaSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Factura

        fields = [
            "id_factura",
            "mes",
            "mes_nombre",
            "anio",
            "fecha_emision",
            "fecha_vencimiento",
            "estado",
            "estado_nombre",
            "total",
            "total_pagado",
            "saldo",
            "detalles",
        ]


class PagoDetalleSerializer(serializers.ModelSerializer):
    concepto = serializers.CharField(
        source="detalle_factura.descripcion",
        read_only=True,
    )

    class Meta:
        model = PagoDetalle

        fields = [
            "id_pago_detalle",
            "concepto",
            "importe_aplicado",
        ]


class ComprobantePagoSerializer(serializers.ModelSerializer):
    archivo_url = serializers.SerializerMethodField()

    class Meta:
        model = ComprobantePago

        fields = [
            "id_comprobante",
            "archivo_url",
            "fecha_subida",
        ]

    def get_archivo_url(
        self,
        obj,
    ):
        request = self.context.get("request")

        if not obj.archivo:
            return None

        if request is None:
            return obj.archivo.url

        return request.build_absolute_uri(obj.archivo.url)


class PagoSerializer(serializers.ModelSerializer):
    id_factura = serializers.IntegerField(
        source="factura.id_factura",
        read_only=True,
    )

    mes = serializers.IntegerField(
        source="factura.mes",
        read_only=True,
    )

    mes_nombre = serializers.CharField(
        source="factura.get_mes_display",
        read_only=True,
    )

    anio = serializers.IntegerField(
        source="factura.anio",
        read_only=True,
    )

    estado_nombre = serializers.CharField(
        source="get_estado_display",
        read_only=True,
    )

    detalles_pago = PagoDetalleSerializer(
        many=True,
        read_only=True,
    )

    comprobantes = ComprobantePagoSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Pago

        fields = [
            "id_pago",
            "id_factura",
            "mes",
            "mes_nombre",
            "anio",
            "fecha_transferencia",
            "monto",
            "numero_operacion",
            "estado",
            "estado_nombre",
            "observaciones",
            "fecha_registro",
            "detalles_pago",
            "comprobantes",
        ]
