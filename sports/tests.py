from datetime import date, time

from django.test import TestCase

from academic.models import (
    NivelEducativo,
    Curso,
    Alumno,
    Profesor,
    Horario,
)

from .models import (
    Deporte,
    GrupoDeportivo,
    InscripcionDeporte,
)

from .forms import InscripcionDeporteForm


class InscripcionDeporteTestCase(TestCase):

    def setUp(self):

        # Nivel

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

        # Profesor

        self.profesor = Profesor.objects.create(
            dni="30123456",
            legajo="PROF001",
            nombre="Carlos",
            apellido="Gómez",
            especialidad="Educación Física",
            correo="carlos@test.com",
            telefono="3624111111",
            estado=True
        )

        # Deportes

        self.futbol = Deporte.objects.create(
            nombre="Fútbol",
            descripcion="Fútbol",
            estado=True
        )

        self.voley = Deporte.objects.create(
            nombre="Vóley",
            descripcion="Vóley",
            estado=True
        )

        self.basquet = Deporte.objects.create(
            nombre="Básquet",
            descripcion="Básquet",
            estado=True
        )

        self.handball = Deporte.objects.create(
            nombre="Handball",
            descripcion="Handball",
            estado=True
        )

        # Horarios

        self.horario_futbol = Horario.objects.create(
            dia_semana="LUNES",
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0)
        )

        self.horario_voley = Horario.objects.create(
            dia_semana="MARTES",
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0)
        )

        self.horario_basquet = Horario.objects.create(
            dia_semana="MIERCOLES",
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0)
        )

        # Se superpone con fútbol:
        # fútbol 09:00 - 10:00
        # handball 09:30 - 10:30

        self.horario_handball = Horario.objects.create(
            dia_semana="LUNES",
            hora_inicio=time(9, 30),
            hora_fin=time(10, 30)
        )

        # Grupos

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

        self.grupo_basquet = GrupoDeportivo.objects.create(
            deporte=self.basquet,
            nivel=self.nivel,
            profesor=self.profesor,
            horario=self.horario_basquet,
            estado=True
        )

        self.grupo_handball = GrupoDeportivo.objects.create(
            deporte=self.handball,
            nivel=self.nivel,
            profesor=self.profesor,
            horario=self.horario_handball,
            estado=True
        )


    def test_no_permite_inscripcion_duplicada_mismo_grupo(self):

        InscripcionDeporte.objects.create(
            alumno=self.alumno,
            grupo=self.grupo_futbol,
            estado=True
        )

        form = InscripcionDeporteForm(
            data={
                "alumno": self.alumno.pk,
                "grupo": self.grupo_futbol.pk,
            }
        )

        self.assertFalse(
            form.is_valid()
        )

        self.assertIn(
            "El alumno ya se encuentra inscripto",
            str(form.non_field_errors())
        )


    def test_no_permite_mas_de_dos_deportes(self):

        InscripcionDeporte.objects.create(
            alumno=self.alumno,
            grupo=self.grupo_futbol,
            estado=True
        )

        InscripcionDeporte.objects.create(
            alumno=self.alumno,
            grupo=self.grupo_voley,
            estado=True
        )

        # Intentamos inscribirlo en un tercer deporte

        form = InscripcionDeporteForm(
            data={
                "alumno": self.alumno.pk,
                "grupo": self.grupo_basquet.pk,
            }
        )

        self.assertFalse(
            form.is_valid()
        )

        self.assertIn(
            "El alumno ya participa en dos deportes",
            str(form.non_field_errors())
        )


    def test_no_permite_superposicion_horaria(self):

        InscripcionDeporte.objects.create(
            alumno=self.alumno,
            grupo=self.grupo_futbol,
            estado=True
        )

        # Fútbol:
        # lunes 09:00 - 10:00
        #
        # Handball:
        # lunes 09:30 - 10:30

        form = InscripcionDeporteForm(
            data={
                "alumno": self.alumno.pk,
                "grupo": self.grupo_handball.pk,
            }
        )

        self.assertFalse(
            form.is_valid()
        )

        self.assertIn(
            "se superpone",
            str(form.non_field_errors())
        )