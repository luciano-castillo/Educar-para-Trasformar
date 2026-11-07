from datetime import date, timedelta
from io import BytesIO

from django.core.mail import EmailMessage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from academic.models import Tutor

from .models import (
    Factura,
    NotificacionPago,
)


def es_ultimo_dia_habil_mes(
    fecha: date,
) -> bool:

    # Sábado o domingo no cuentan
    # como día hábil.
    if fecha.weekday() >= 5:
        return False

    siguiente = fecha + timedelta(days=1)

    # Saltamos el fin de semana.
    while siguiente.weekday() >= 5:
        siguiente += timedelta(days=1)

    # Si el próximo día hábil pertenece
    # a otro mes, hoy es el último hábil.
    return siguiente.month != fecha.month


def construir_resumen_factura(
    factura,
):

    lineas = [
        (
            f"Alumno: "
            f"{factura.alumno.apellido}, "
            f"{factura.alumno.nombre}"
        ),
        (
            f"Período: "
            f"{factura.get_mes_display()} "
            f"{factura.anio}"
        ),
        "",
        "Composición:",
    ]

    for detalle in factura.detalles.all():

        lineas.append(
            
                f"- {detalle.descripcion}: "
                f"${detalle.importe:.2f}"
            
        )

    lineas.extend(
        [
            "",
            f"Total: ${factura.total:.2f}",
            f"Pagado: ${factura.total_pagado:.2f}",
            f"Saldo: ${factura.saldo:.2f}",
            (
                "Fecha de vencimiento: "
                f"{factura.fecha_vencimiento:%d/%m/%Y}"
            ),
        ]
    )

    return "\n".join(lineas)

def generar_factura_pdf(
    factura,
):
    buffer = BytesIO()

    documento = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    estilos = getSampleStyleSheet()

    elementos = [
        Paragraph(
            "Educar para Transformar",
            estilos["Title"],
        ),
        Spacer(
            1,
            0.4 * cm,
        ),
        Paragraph(
            f"Factura N° {factura.id_factura}",
            estilos["Heading2"],
        ),
        Spacer(
            1,
            0.3 * cm,
        ),
        Paragraph(
            (
                f"<b>Alumno:</b> "
                f"{factura.alumno.apellido}, "
                f"{factura.alumno.nombre}"
            ),
            estilos["BodyText"],
        ),
        Paragraph(
            (
                f"<b>Período:</b> "
                f"{factura.get_mes_display()} "
                f"{factura.anio}"
            ),
            estilos["BodyText"],
        ),
        Paragraph(
            (
                f"<b>Vencimiento:</b> "
                f"{factura.fecha_vencimiento:%d/%m/%Y}"
            ),
            estilos["BodyText"],
        ),
        Spacer(
            1,
            0.6 * cm,
        ),
    ]

    datos = [
        [
            "Concepto",
            "Importe",
        ]
    ]

    for detalle in factura.detalles.all():
        datos.append(
            [
                detalle.descripcion,
                f"$ {detalle.importe:.2f}",
            ]
        )

    tabla = Table(
        datos,
        colWidths=[
            12 * cm,
            4 * cm,
        ],
    )

    tabla.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "ALIGN",
                    (1, 1),
                    (1, -1),
                    "RIGHT",
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    elementos.append(
        tabla
    )

    elementos.extend(
        [
            Spacer(
                1,
                0.6 * cm,
            ),
            Paragraph(
                (
                    f"<b>Total:</b> "
                    f"$ {factura.total:.2f}"
                ),
                estilos["BodyText"],
            ),
            Paragraph(
                (
                    f"<b>Pagado:</b> "
                    f"$ {factura.total_pagado:.2f}"
                ),
                estilos["BodyText"],
            ),
            Paragraph(
                (
                    f"<b>Saldo pendiente:</b> "
                    f"$ {factura.saldo:.2f}"
                ),
                estilos["BodyText"],
            ),
        ]
    )

    documento.build(
        elementos
    )

    pdf = buffer.getvalue()

    buffer.close()

    return pdf

def enviar_recordatorios_pago(
    mes,
    anio,
):

    facturas = (
        Factura.objects
        .filter(
            mes=mes,
            anio=anio,
        )
        .exclude(
            estado__in=[
                "PAGADA",
                "ANULADA",
            ]
        )
        .select_related(
            "alumno"
        )
        .prefetch_related(
            "detalles"
        )
    )

    cantidad_enviada = 0

    for factura in facturas:

        tutores = (
            Tutor.objects
            .filter(
                alumnos_asociados__alumno=(
                    factura.alumno
                ),
                estado=True,
            )
            .exclude(
                correo=""
            )
            .distinct()
        )

        resumen = construir_resumen_factura(
            factura
        )
        pdf_factura = generar_factura_pdf(
            factura
        )

        for tutor in tutores:
            if NotificacionPago.objects.filter(
                factura=factura,
                tutor=tutor,
                tipo="RECORDATORIO",
            ).exists():

                continue

            cuerpo = (
                f"Hola {tutor.nombre},\n\n"
                "Le enviamos el detalle mensual "
                "correspondiente a:\n\n"
                f"{resumen}\n\n"
                "Educar para Transformar"
            )

            email = EmailMessage(
                subject=(
                    "Recordatorio mensual de pago - "
                    f"{factura.get_mes_display()} "
                    f"{factura.anio}"
                ),
                body=cuerpo,
                to=[
                    tutor.correo
                ],
            )

            # Adjuntamos también el detalle
            # de la factura como archivo.
            email.attach(
                (
                    f"factura_"
                    f"{factura.id_factura}.pdf"
                ),
                pdf_factura,
                "application/pdf",
            )

            email.send()
            NotificacionPago.objects.create(
                factura=factura,
                tutor=tutor,
                tipo="RECORDATORIO",
            )

            cantidad_enviada += 1

    return cantidad_enviada

def enviar_avisos_deuda(
    mes,
    anio,
):

    facturas = (
        Factura.objects
        .filter(
            mes=mes,
            anio=anio,
        )
        .exclude(
            estado__in=[
                "PAGADA",
                "ANULADA",
            ]
        )
        .select_related(
            "alumno"
        )
        .prefetch_related(
            "detalles"
        )
    )

    cantidad_enviada = 0

    for factura in facturas:

        # No alcanza con mirar el estado:
        # verificamos que realmente exista deuda.
        if factura.saldo <= 0:
            continue

        tutores = (
            Tutor.objects
            .filter(
                alumnos_asociados__alumno=(
                    factura.alumno
                ),
                estado=True,
            )
            .exclude(
                correo=""
            )
            .distinct()
        )

        for tutor in tutores:
            if NotificacionPago.objects.filter(
                factura=factura,
                tutor=tutor,
                tipo="DEUDA",
            ).exists():

                continue

            cuerpo = (
                f"Hola {tutor.nombre},\n\n"
                "Le informamos que todavía existe "
                "un saldo pendiente correspondiente a:\n\n"
                f"Alumno: "
                f"{factura.alumno.apellido}, "
                f"{factura.alumno.nombre}\n"
                f"Período: "
                f"{factura.get_mes_display()} "
                f"{factura.anio}\n"
                f"Total de la factura: "
                f"${factura.total:.2f}\n"
                f"Total abonado: "
                f"${factura.total_pagado:.2f}\n"
                f"Saldo pendiente: "
                f"${factura.saldo:.2f}\n"
                f"Fecha de vencimiento: "
                f"{factura.fecha_vencimiento:%d/%m/%Y}\n\n"
                "Educar para Transformar"
            )

            email = EmailMessage(
                subject=(
                    "Aviso de deuda pendiente - "
                    f"{factura.get_mes_display()} "
                    f"{factura.anio}"
                ),
                body=cuerpo,
                to=[
                    tutor.correo
                ],
            )

            email.send()
            NotificacionPago.objects.create(
                factura=factura,
                tutor=tutor,
                tipo="DEUDA",
            )

            cantidad_enviada += 1

    return cantidad_enviada