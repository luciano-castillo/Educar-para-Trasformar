from rest_framework import serializers

from academic.models import Alumno, Curso
from billing.models import (
    DetalleFactura,
    Factura,
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

    class Meta:
        model = DetalleFactura

        fields = [
            "id_detalle",
            "tipo_concepto",
            "descripcion",
            "importe",
            "total_pagado",
            "saldo_pendiente",
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
