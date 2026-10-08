from datetime import date

from django.test import TestCase

from academic.models import (
    NivelEducativo,
    Curso,
    Alumno,
)

from .models import (
    RutaTransporte,
    ContratacionTransporte,
    ServicioComedor,
    ContratacionComedor,
)

from .forms import (
    RutaTransporteForm,
    ContratacionTransporteForm,
    ServicioComedorForm,
    ContratacionComedorForm,
)


class ServiciosTestCase(TestCase):

    def setUp(self):

        # Nivel educativo

        self.nivel = NivelEducativo.objects.create(
            nombre="Primario",
            estado=True
        )

        # Curso

        self.curso = Curso.objects.create(
            nombre="1°",
            division="A",
            turno="MANANA",
            nivel=self.nivel,
            estado=True
        )

        # Alumno

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

        # Rutas

        self.ruta_centro = RutaTransporte.objects.create(
            nombre="Zona Centro",
            descripcion="Recorrido zona centro",
            valor_mensual=45000,
            estado=True
        )

        self.ruta_norte = RutaTransporte.objects.create(
            nombre="Zona Norte",
            descripcion="Recorrido zona norte",
            valor_mensual=48000,
            estado=True
        )

        # Comedor

        self.comedor = ServicioComedor.objects.create(
            nombre="Comedor Escolar",
            descripcion="Servicio de comedor",
            valor_mensual=65000,
            estado=True
        )
    
    def test_ruta_no_permite_valor_cero(self):

        form = RutaTransporteForm(
            data={
                "nombre": "Ruta prueba",
                "descripcion": "Ruta para test",
                "valor_mensual": 0,
                "estado": True,
            }
        )

        self.assertFalse(
            form.is_valid()
        )
        
    def test_comedor_no_permite_valor_cero(self):

        form = ServicioComedorForm(
            data={
                "nombre": "Comedor prueba",
                "descripcion": "Servicio para test",
                "valor_mensual": 0,
                "estado": True,
            }
        )

        self.assertFalse(
            form.is_valid()
        )
    
    def test_alumno_no_puede_tener_dos_transportes_mismo_periodo(self):

        ContratacionTransporte.objects.create(
            alumno=self.alumno,
            ruta=self.ruta_centro,
            mes=3,
            anio=2027,
            estado=True
        )

        form = ContratacionTransporteForm(
            data={
                "alumno": self.alumno.pk,
                "ruta": self.ruta_norte.pk,
                "mes": 3,
                "anio": 2027,
                "estado": True,
            }
        )

        self.assertFalse(
            form.is_valid()
        )
        
    def test_alumno_no_puede_tener_dos_comedores_mismo_periodo(self):

        ContratacionComedor.objects.create(
            alumno=self.alumno,
            servicio=self.comedor,
            mes=3,
            anio=2027,
            estado=True
        )

        form = ContratacionComedorForm(
            data={
                "alumno": self.alumno.pk,
                "servicio": self.comedor.pk,
                "mes": 3,
                "anio": 2027,
                "estado": True,
            }
        )

        self.assertFalse(
            form.is_valid()
        )