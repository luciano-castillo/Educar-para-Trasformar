from django.core.management.base import (
    BaseCommand,
    CommandError,
)
from django.utils import timezone

from billing.notifications import (
    enviar_recordatorios_pago,
    es_ultimo_dia_habil_mes,
)


class Command(BaseCommand):

    help = (
        "Envía los recordatorios mensuales "
        "de pago a los tutores."
    )

    def add_arguments(
        self,
        parser,
    ):

        parser.add_argument(
            "--mes",
            type=int,
            help="Mes de la factura a notificar.",
        )

        parser.add_argument(
            "--anio",
            type=int,
            help="Año de la factura a notificar.",
        )

        parser.add_argument(
            "--forzar",
            action="store_true",
            help=(
                "Ejecuta el envío aunque hoy "
                "no sea el último día hábil."
            ),
        )

    def handle(
        self,
        *args,
        **options,
    ):

        hoy = timezone.localdate()

        mes = (
            options["mes"]
            or hoy.month
        )

        anio = (
            options["anio"]
            or hoy.year
        )

        if not 1 <= mes <= 12:

            raise CommandError(
                "El mes debe estar entre 1 y 12."
            )

        if (
            not options["forzar"]
            and
            not es_ultimo_dia_habil_mes(
                hoy
            )
        ):

            self.stdout.write(
                self.style.WARNING(
                    "Hoy no es el último día "
                    "hábil del mes. "
                    "No se enviaron recordatorios."
                )
            )

            return

        cantidad = enviar_recordatorios_pago(
            mes=mes,
            anio=anio,
        )

        self.stdout.write(
            self.style.SUCCESS(
                
                    "Proceso finalizado. "
                    f"Correos enviados: {cantidad}."
                
            )
        )