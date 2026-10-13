from datetime import date

from django.db import IntegrityError, transaction
from django.test import TestCase

from .models import CuotaMensual
from .forms import CuotaMensualForm


class CuotaMensualTestCase(TestCase):

    def setUp(self):

        self.cuota_octubre = CuotaMensual.objects.create(
            mes=10,
            anio=2026,
            valor=55000,
            fecha_vencimiento=date(2026, 10, 10),
            estado=True
        )


    def test_no_permite_valor_cero(self):

        form = CuotaMensualForm(
            data={
                "mes": 11,
                "anio": 2026,
                "valor": 0,
                "fecha_vencimiento": "2026-11-10",
                "estado": True,
            }
        )

        self.assertFalse(
            form.is_valid()
        )

        self.assertIn(
            "El valor de la cuota debe ser mayor a cero.",
            str(form.errors)
        )


    def test_no_permite_periodo_duplicado(self):

        form = CuotaMensualForm(
            data={
                "mes": 10,
                "anio": 2026,
                "valor": 60000,
                "fecha_vencimiento": "2026-10-15",
                "estado": True,
            }
        )

        self.assertFalse(
            form.is_valid()
        )

        self.assertIn(
            "Ya existe una cuota registrada",
            str(form.non_field_errors())
        )


    def test_permite_periodo_diferente(self):

        form = CuotaMensualForm(
            data={
                "mes": 11,
                "anio": 2026,
                "valor": 60000,
                "fecha_vencimiento": "2026-11-10",
                "estado": True,
            }
        )

        self.assertTrue(
            form.is_valid()
        )


    def test_permite_editar_misma_cuota(self):

        form = CuotaMensualForm(
            data={
                "mes": 10,
                "anio": 2026,
                "valor": 58000,
                "fecha_vencimiento": "2026-10-10",
                "estado": True,
            },
            instance=self.cuota_octubre
        )

        self.assertTrue(
            form.is_valid()
        )


    def test_base_datos_impide_periodo_duplicado(self):

        with self.assertRaises(
            IntegrityError
        ):

            with transaction.atomic():

                CuotaMensual.objects.create(
                    mes=10,
                    anio=2026,
                    valor=70000,
                    fecha_vencimiento=date(
                        2026,
                        10,
                        20
                    ),
                    estado=True
                )