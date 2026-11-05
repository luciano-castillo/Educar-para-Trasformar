from django.core.management.base import BaseCommand
from django.utils import timezone

from billing.notifications import (
    enviar_avisos_deuda,
    enviar_recordatorios_pago,
    es_ultimo_dia_habil_mes,
)


class Command(BaseCommand):

    help = (
        "Procesa automáticamente las "
        "notificaciones de pagos del día."
    )

    def handle(
        self,
        *args,
        **options,
    ):

        hoy = timezone.localdate()

        proceso_ejecutado = False

        # -----------------------------------------
        # RF56
        # Día 20: avisar deudas pendientes
        # -----------------------------------------

        if hoy.day == 20:

            cantidad_deuda = (
                enviar_avisos_deuda(
                    mes=hoy.month,
                    anio=hoy.year,
                )
            )

            self.stdout.write(
                self.style.SUCCESS(
                    
                        "RF56 - Avisos de deuda "
                        f"enviados: {cantidad_deuda}."
                    
                )
            )

            proceso_ejecutado = True

        # -----------------------------------------
        # RF55
        # Último día hábil:
        # recordatorio mensual
        # -----------------------------------------

        if es_ultimo_dia_habil_mes(
            hoy
        ):

            cantidad_recordatorios = (
                enviar_recordatorios_pago(
                    mes=hoy.month,
                    anio=hoy.year,
                )
            )

            self.stdout.write(
                self.style.SUCCESS(
                    
                        "RF55 - Recordatorios "
                        "mensuales enviados: "
                        f"{cantidad_recordatorios}."
                    
                )
            )

            proceso_ejecutado = True

        # -----------------------------------------
        # Día sin notificaciones programadas
        # -----------------------------------------

        if not proceso_ejecutado:

            self.stdout.write(
                self.style.WARNING(
                    
                        "Hoy no corresponde ejecutar "
                        "ninguna notificación de pago."
                    
                )
            )