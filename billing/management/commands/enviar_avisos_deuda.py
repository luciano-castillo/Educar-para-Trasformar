from django.core.management.base import (
    BaseCommand,
    CommandError,
)
from django.utils import timezone

from billing.notifications import (
    enviar_avisos_deuda,
)


class Command(BaseCommand):

    help = (
        "Envía avisos de deuda pendiente "
        "a los tutores el día 20."
    )

    def add_arguments(
        self,
        parser,
    ):

        parser.add_argument(
            "--mes",
            type=int,
            help="Mes de la deuda a notificar.",
        )

        parser.add_argument(
            "--anio",
            type=int,
            help="Año de la deuda a notificar.",
        )

        parser.add_argument(
            "--forzar",
            action="store_true",
            help=(
                "Ejecuta el envío aunque hoy "
                "no sea día 20."
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
            hoy.day != 20
        ):

            self.stdout.write(
                self.style.WARNING(
                    "Hoy no es día 20. "
                    "No se enviaron avisos de deuda."
                )
            )

            return

        cantidad = enviar_avisos_deuda(
            mes=mes,
            anio=anio,
        )

        self.stdout.write(
            self.style.SUCCESS(
                
                    "Proceso finalizado. "
                    f"Avisos enviados: {cantidad}."
                
            )
        )