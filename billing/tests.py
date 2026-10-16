from datetime import date, time

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from academic.models import (
    NivelEducativo,
    Curso,
    Alumno,
    Profesor,
    Horario,
)

from sports.models import (
    Deporte,
    GrupoDeportivo,
    InscripcionDeporte,
)

from services.models import (
    RutaTransporte,
    ContratacionTransporte,
    ServicioComedor,
    ContratacionComedor,
)

from .models import (
    CuotaMensual,
    Factura,
)

from .forms import CuotaMensualForm
from .services import generar_factura_alumno


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

class GeneracionFacturaTestCase(TestCase):

    def setUp(self):

        # ---------------------------------------------
        # Nivel y curso
        # ---------------------------------------------

        self.nivel = NivelEducativo.objects.create(
            nombre="Primario",
            estado=True
        )

        self.curso = Curso.objects.create(
            nombre="1°",
            division="A",
            turno="MANANA",
            nivel=self.nivel,
            estado=True
        )

        # ---------------------------------------------
        # Alumno principal
        # ---------------------------------------------

        self.alumno = Alumno.objects.create(
            dni="45123456",
            legajo="ALU001",
            nombre="Lucía",
            apellido="Martínez",
            fecha_nacimiento=date(2015, 5, 10),
            domicilio="Calle 123",
            telefono="3624000000",
            correo="lucia@test.com",
            curso=self.curso,
            estado=True
        )

        # Alumno sin servicios opcionales

        self.alumno_sin_servicios = Alumno.objects.create(
            dni="45999999",
            legajo="ALU002",
            nombre="Juan",
            apellido="Pérez",
            fecha_nacimiento=date(2015, 7, 15),
            domicilio="Calle 456",
            telefono="3624111111",
            correo="juan@test.com",
            curso=self.curso,
            estado=True
        )

        # ---------------------------------------------
        # Cuota octubre 2026
        # ---------------------------------------------

        self.cuota = CuotaMensual.objects.create(
            mes=10,
            anio=2026,
            valor=55000,
            fecha_vencimiento=date(
                2026,
                10,
                10
            ),
            estado=True
        )

        # ---------------------------------------------
        # Profesor
        # ---------------------------------------------

        self.profesor = Profesor.objects.create(
            dni="30123456",
            legajo="PROF001",
            nombre="Carlos",
            apellido="Gómez",
            especialidad="Educación Física",
            correo="carlos@test.com",
            telefono="3624222222",
            estado=True
        )

        # ---------------------------------------------
        # Horarios
        # ---------------------------------------------

        self.horario_futbol = Horario.objects.create(
            dia_semana="LUNES",
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0)
        )

        self.horario_voley = Horario.objects.create(
            dia_semana="MARTES",
            hora_inicio=time(10, 0),
            hora_fin=time(11, 0)
        )

        # ---------------------------------------------
        # Deportes
        # ---------------------------------------------

        self.futbol = Deporte.objects.create(
            nombre="Fútbol",
            descripcion="Fútbol escolar",
            valor_mensual=20000,
            estado=True
        )

        self.voley = Deporte.objects.create(
            nombre="Vóley",
            descripcion="Vóley escolar",
            valor_mensual=18000,
            estado=True
        )

        # ---------------------------------------------
        # Grupos
        # ---------------------------------------------

        self.grupo_futbol = GrupoDeportivo.objects.create(
            deporte=self.futbol,
            nivel=self.nivel,
            profesor=self.profesor,
            horario=self.horario_futbol,
            estado=True
        )

        self.grupo_voley = GrupoDeportivo.objects.create(
            deporte=self.voley,
            nivel=self.nivel,
            profesor=self.profesor,
            horario=self.horario_voley,
            estado=True
        )

        # ---------------------------------------------
        # Inscripciones deportivas
        # ---------------------------------------------

        inscripcion_futbol = (
            InscripcionDeporte.objects.create(
                alumno=self.alumno,
                grupo=self.grupo_futbol,
                estado=True
            )
        )

        inscripcion_voley = (
            InscripcionDeporte.objects.create(
                alumno=self.alumno,
                grupo=self.grupo_voley,
                estado=True
            )
        )

        # auto_now_add coloca la fecha actual.
        # La cambiamos para que el test sea siempre
        # independiente de la fecha en que se ejecute.

        InscripcionDeporte.objects.filter(
            pk=inscripcion_futbol.pk
        ).update(
            fecha_inscripcion=date(
                2026,
                10,
                1
            )
        )

        InscripcionDeporte.objects.filter(
            pk=inscripcion_voley.pk
        ).update(
            fecha_inscripcion=date(
                2026,
                10,
                1
            )
        )

        # ---------------------------------------------
        # Transporte
        # ---------------------------------------------

        self.ruta = RutaTransporte.objects.create(
            nombre="Zona Centro",
            descripcion="Recorrido zona centro",
            valor_mensual=30000,
            estado=True
        )

        ContratacionTransporte.objects.create(
            alumno=self.alumno,
            ruta=self.ruta,
            mes=10,
            anio=2026,
            estado=True
        )

        # ---------------------------------------------
        # Comedor
        # ---------------------------------------------

        self.comedor = ServicioComedor.objects.create(
            nombre="Comedor Escolar",
            descripcion="Servicio mensual",
            valor_mensual=25000,
            estado=True
        )

        ContratacionComedor.objects.create(
            alumno=self.alumno,
            servicio=self.comedor,
            mes=10,
            anio=2026,
            estado=True
        )


    def test_genera_factura_con_todos_los_conceptos(self):

        factura = generar_factura_alumno(
            alumno=self.alumno,
            mes=10,
            anio=2026
        )

        self.assertEqual(
            factura.detalles.count(),
            5
        )

        tipos = list(
            factura.detalles.values_list(
                "tipo_concepto",
                flat=True
            )
        )

        self.assertEqual(
            tipos.count("CUOTA"),
            1
        )

        self.assertEqual(
            tipos.count("DEPORTE"),
            2
        )

        self.assertEqual(
            tipos.count("TRANSPORTE"),
            1
        )

        self.assertEqual(
            tipos.count("COMEDOR"),
            1
        )

        self.assertEqual(
            factura.total,
            148000
        )


    def test_alumno_sin_servicios_genera_solo_cuota(self):

        factura = generar_factura_alumno(
            alumno=self.alumno_sin_servicios,
            mes=10,
            anio=2026
        )

        self.assertEqual(
            factura.detalles.count(),
            1
        )

        detalle = factura.detalles.first()

        self.assertEqual(
            detalle.tipo_concepto,
            "CUOTA"
        )

        self.assertEqual(
            factura.total,
            55000
        )


    def test_no_permite_factura_duplicada(self):

        generar_factura_alumno(
            alumno=self.alumno,
            mes=10,
            anio=2026
        )

        with self.assertRaises(
            ValidationError
        ):

            generar_factura_alumno(
                alumno=self.alumno,
                mes=10,
                anio=2026
            )

        self.assertEqual(
            Factura.objects.filter(
                alumno=self.alumno,
                mes=10,
                anio=2026
            ).count(),
            1
        )


    def test_factura_conserva_precios_historicos(self):

        factura = generar_factura_alumno(
            alumno=self.alumno,
            mes=10,
            anio=2026
        )

        total_original = factura.total

        # Cambiamos todos los valores originales

        self.cuota.valor = 99999
        self.cuota.save()

        self.futbol.valor_mensual = 99999
        self.futbol.save()

        self.voley.valor_mensual = 99999
        self.voley.save()

        self.ruta.valor_mensual = 99999
        self.ruta.save()

        self.comedor.valor_mensual = 99999
        self.comedor.save()

        factura.refresh_from_db()

        self.assertEqual(
            factura.total,
            total_original
        )

        self.assertEqual(
            factura.total,
            148000
        )


    def test_error_revierte_factura_completa(self):

        # Eliminamos la contratación válida
        # de transporte.

        ContratacionTransporte.objects.filter(
            alumno=self.alumno,
            mes=10,
            anio=2026
        ).delete()

        # Creamos una ruta con precio inválido.
        # Lo hacemos directamente desde el modelo
        # para simular un dato incorrecto en la BD.

        ruta_invalida = RutaTransporte.objects.create(
            nombre="Ruta inválida",
            descripcion="Prueba rollback",
            valor_mensual=0,
            estado=True
        )

        ContratacionTransporte.objects.create(
            alumno=self.alumno,
            ruta=ruta_invalida,
            mes=10,
            anio=2026,
            estado=True
        )

        with self.assertRaises(
            ValidationError
        ):

            generar_factura_alumno(
                alumno=self.alumno,
                mes=10,
                anio=2026
            )

        # Gracias a @transaction.atomic,
        # la factura creada parcialmente
        # también debe desaparecer.

        self.assertFalse(
            Factura.objects.filter(
                alumno=self.alumno,
                mes=10,
                anio=2026
            ).exists()
        )