from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import (
    IntegrityError,
    transaction,
)
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import PerfilUsuario

from .models import (
    Alumno,
    Asistencia,
    Curso,
    DictadoMateria,
    Horario,
    Materia,
    NivelEducativo,
    Nota,
    Profesor,
    Tutor,
    TutorAlumno,
)
from .services import registrar_asistencias, registrar_notas


class AsistenciaTestCase(TestCase):

    def setUp(self):

        # -----------------------------------------
        # Usuarios docentes
        # -----------------------------------------

        self.usuario_docente = (
            User.objects.create_user(
                username="docente1",
                password="123456"
            )
        )

        PerfilUsuario.objects.create(
            usuario=self.usuario_docente,
            rol=PerfilUsuario.Rol.DOCENTE
        )

        self.usuario_otro_docente = (
            User.objects.create_user(
                username="docente2",
                password="123456"
            )
        )

        PerfilUsuario.objects.create(
            usuario=self.usuario_otro_docente,
            rol=PerfilUsuario.Rol.DOCENTE
        )

        # -----------------------------------------
        # Nivel y cursos
        # -----------------------------------------

        self.nivel = NivelEducativo.objects.create(
            nombre="Secundario",
            estado=True
        )

        self.curso = Curso.objects.create(
            nombre="2°",
            division="A",
            turno="MANANA",
            nivel=self.nivel,
            estado=True
        )

        self.otro_curso = Curso.objects.create(
            nombre="2°",
            division="B",
            turno="MANANA",
            nivel=self.nivel,
            estado=True
        )

        # -----------------------------------------
        # Profesores
        # -----------------------------------------

        self.profesor = Profesor.objects.create(
            usuario=self.usuario_docente,
            dni="11111111",
            legajo="PROF001",
            nombre="Ana",
            apellido="Gómez",
            especialidad="Matemática",
            correo="ana@test.com",
            telefono="111111",
            estado=True
        )

        self.otro_profesor = Profesor.objects.create(
            usuario=self.usuario_otro_docente,
            dni="22222222",
            legajo="PROF002",
            nombre="Carlos",
            apellido="Pérez",
            especialidad="Matemática",
            correo="carlos@test.com",
            telefono="222222",
            estado=True
        )

        # -----------------------------------------
        # Materia y horario
        # -----------------------------------------

        self.materia = Materia.objects.create(
            nombre="Matemática",
            estado=True
        )

        self.horario = Horario.objects.create(
            dia_semana="LUNES",
            hora_inicio="08:00",
            hora_fin="09:00"
        )

        # -----------------------------------------
        # Dictado
        # -----------------------------------------

        self.dictado = DictadoMateria.objects.create(
            materia=self.materia,
            profesor=self.profesor,
            curso=self.curso,
            horario=self.horario
        )

        # -----------------------------------------
        # Alumnos del curso
        # -----------------------------------------

        self.alumno1 = Alumno.objects.create(
            dni="33333333",
            legajo="ALU001",
            nombre="Juan",
            apellido="López",
            fecha_nacimiento="2012-01-10",
            domicilio="Calle 1",
            telefono="333333",
            correo="juan@test.com",
            curso=self.curso,
            estado=True
        )

        self.alumno2 = Alumno.objects.create(
            dni="44444444",
            legajo="ALU002",
            nombre="María",
            apellido="Fernández",
            fecha_nacimiento="2012-02-15",
            domicilio="Calle 2",
            telefono="444444",
            correo="maria@test.com",
            curso=self.curso,
            estado=True
        )

        self.alumno_otro_curso = (
            Alumno.objects.create(
                dni="55555555",
                legajo="ALU003",
                nombre="Pedro",
                apellido="Martínez",
                fecha_nacimiento="2012-03-20",
                domicilio="Calle 3",
                telefono="555555",
                correo="pedro@test.com",
                curso=self.otro_curso,
                estado=True
            )
        )

        self.fecha = (
            timezone.localdate()
            - timedelta(days=1)
        )


    def test_registra_asistencias_correctamente(self):

        asistencias = registrar_asistencias(
            profesor=self.profesor,
            dictado=self.dictado,
            fecha=self.fecha,
            registros=[
                {
                    "alumno": self.alumno1,
                    "estado": "PRESENTE",
                    "observaciones": ""
                },
                {
                    "alumno": self.alumno2,
                    "estado": "AUSENTE",
                    "observaciones": "Sin aviso"
                },
            ]
        )

        self.assertEqual(
            len(asistencias),
            2
        )

        self.assertEqual(
            Asistencia.objects.filter(
                dictado=self.dictado,
                fecha=self.fecha
            ).count(),
            2
        )

        asistencia1 = Asistencia.objects.get(
            alumno=self.alumno1,
            dictado=self.dictado,
            fecha=self.fecha
        )

        self.assertEqual(
            asistencia1.estado,
            "PRESENTE"
        )


    def test_actualiza_asistencia_sin_duplicar(self):

        registrar_asistencias(
            profesor=self.profesor,
            dictado=self.dictado,
            fecha=self.fecha,
            registros=[
                {
                    "alumno": self.alumno1,
                    "estado": "PRESENTE",
                    "observaciones": ""
                }
            ]
        )

        registrar_asistencias(
            profesor=self.profesor,
            dictado=self.dictado,
            fecha=self.fecha,
            registros=[
                {
                    "alumno": self.alumno1,
                    "estado": "TARDE",
                    "observaciones": "Llegó 10 minutos tarde"
                }
            ]
        )

        self.assertEqual(
            Asistencia.objects.filter(
                alumno=self.alumno1,
                dictado=self.dictado,
                fecha=self.fecha
            ).count(),
            1
        )

        asistencia = Asistencia.objects.get(
            alumno=self.alumno1,
            dictado=self.dictado,
            fecha=self.fecha
        )

        self.assertEqual(
            asistencia.estado,
            "TARDE"
        )

        self.assertEqual(
            asistencia.observaciones,
            "Llegó 10 minutos tarde"
        )


    def test_no_permite_profesor_de_otro_dictado(self):

        with self.assertRaises(
            ValidationError
        ):

            registrar_asistencias(
                profesor=self.otro_profesor,
                dictado=self.dictado,
                fecha=self.fecha,
                registros=[
                    {
                        "alumno": self.alumno1,
                        "estado": "PRESENTE",
                        "observaciones": ""
                    }
                ]
            )

        self.assertFalse(
            Asistencia.objects.exists()
        )


    def test_no_permite_alumno_de_otro_curso(self):

        with self.assertRaises(
            ValidationError
        ):

            registrar_asistencias(
                profesor=self.profesor,
                dictado=self.dictado,
                fecha=self.fecha,
                registros=[
                    {
                        "alumno": (
                            self.alumno_otro_curso
                        ),
                        "estado": "PRESENTE",
                        "observaciones": ""
                    }
                ]
            )

        self.assertFalse(
            Asistencia.objects.exists()
        )


    def test_no_permite_fecha_futura(self):

        fecha_futura = (
            timezone.localdate()
            + timedelta(days=1)
        )

        with self.assertRaises(
            ValidationError
        ):

            registrar_asistencias(
                profesor=self.profesor,
                dictado=self.dictado,
                fecha=fecha_futura,
                registros=[
                    {
                        "alumno": self.alumno1,
                        "estado": "PRESENTE",
                        "observaciones": ""
                    }
                ]
            )

        self.assertFalse(
            Asistencia.objects.exists()
        )


    def test_restriccion_impide_asistencia_duplicada(self):

        Asistencia.objects.create(
            alumno=self.alumno1,
            dictado=self.dictado,
            fecha=self.fecha,
            estado="PRESENTE"
        )

        with self.assertRaises(
            IntegrityError
        ), transaction.atomic():

            Asistencia.objects.create(
                alumno=self.alumno1,
                dictado=self.dictado,
                fecha=self.fecha,
                estado="AUSENTE"
            )


    def test_docente_registra_desde_interfaz(self):

        self.client.force_login(
            self.usuario_docente
        )

        response = self.client.post(
            reverse(
                "asistencia_tomar",
                args=[
                    self.dictado.id_dictado
                ]
            ),
            {
                "fecha": self.fecha.isoformat(),

                (
                    f"estado_"
                    f"{self.alumno1.id_alumno}"
                ): "PRESENTE",

                (
                    f"observaciones_"
                    f"{self.alumno1.id_alumno}"
                ): "",

                (
                    f"estado_"
                    f"{self.alumno2.id_alumno}"
                ): "AUSENTE",

                (
                    f"observaciones_"
                    f"{self.alumno2.id_alumno}"
                ): "Faltó",
            }
        )

        self.assertEqual(
            response.status_code,
            302
        )

        self.assertEqual(
            Asistencia.objects.filter(
                dictado=self.dictado,
                fecha=self.fecha
            ).count(),
            2
        )

        asistencia = Asistencia.objects.get(
            alumno=self.alumno2,
            dictado=self.dictado,
            fecha=self.fecha
        )

        self.assertEqual(
            asistencia.estado,
            "AUSENTE"
        )


    def test_docente_no_accede_dictado_ajeno(self):

        self.client.force_login(
            self.usuario_otro_docente
        )

        response = self.client.get(
            reverse(
                "asistencia_tomar",
                args=[
                    self.dictado.id_dictado
                ]
            )
        )

        self.assertEqual(
            response.status_code,
            404
        )

        response_historial = self.client.get(
            reverse(
                "asistencia_historial",
                args=[
                    self.dictado.id_dictado
                ]
            )
        )

        self.assertEqual(
            response_historial.status_code,
            404
        )


    def test_historial_resume_estados_por_fecha(self):

        registrar_asistencias(
            profesor=self.profesor,
            dictado=self.dictado,
            fecha=self.fecha,
            registros=[
                {
                    "alumno": self.alumno1,
                    "estado": "PRESENTE",
                    "observaciones": ""
                },
                {
                    "alumno": self.alumno2,
                    "estado": "AUSENTE",
                    "observaciones": ""
                },
            ]
        )

        self.client.force_login(
            self.usuario_docente
        )

        response = self.client.get(
            reverse(
                "asistencia_historial",
                args=[
                    self.dictado.id_dictado
                ]
            )
        )

        self.assertEqual(
            response.status_code,
            200
        )

        historial = list(
            response.context[
                "historial"
            ]
        )

        self.assertEqual(
            len(historial),
            1
        )

        fila = historial[0]

        self.assertEqual(
            fila["total"],
            2
        )

        self.assertEqual(
            fila["presentes"],
            1
        )

        self.assertEqual(
            fila["ausentes"],
            1
        )

        self.assertEqual(
            fila["tardes"],
            0
        )

        self.assertEqual(
            fila["justificados"],
            0
        )


class NotaTestCase(TestCase):

    def setUp(self):

        # -----------------------------------------
        # Usuarios docentes
        # -----------------------------------------

        self.usuario_docente = (
            User.objects.create_user(
                username="docente_notas",
                password="123456"
            )
        )

        PerfilUsuario.objects.create(
            usuario=self.usuario_docente,
            rol=PerfilUsuario.Rol.DOCENTE
        )

        self.usuario_otro_docente = (
            User.objects.create_user(
                username="otro_docente_notas",
                password="123456"
            )
        )

        PerfilUsuario.objects.create(
            usuario=self.usuario_otro_docente,
            rol=PerfilUsuario.Rol.DOCENTE
        )

        # -----------------------------------------
        # Nivel y cursos
        # -----------------------------------------

        self.nivel = NivelEducativo.objects.create(
            nombre="Secundario",
            estado=True
        )

        self.curso = Curso.objects.create(
            nombre="3°",
            division="A",
            turno="MANANA",
            nivel=self.nivel,
            estado=True
        )

        self.otro_curso = Curso.objects.create(
            nombre="3°",
            division="B",
            turno="MANANA",
            nivel=self.nivel,
            estado=True
        )

        # -----------------------------------------
        # Profesores
        # -----------------------------------------

        self.profesor = Profesor.objects.create(
            usuario=self.usuario_docente,
            dni="61111111",
            legajo="PROFN001",
            nombre="Laura",
            apellido="Gómez",
            especialidad="Matemática",
            correo="laura@test.com",
            telefono="111111",
            estado=True
        )

        self.otro_profesor = Profesor.objects.create(
            usuario=self.usuario_otro_docente,
            dni="62222222",
            legajo="PROFN002",
            nombre="Martín",
            apellido="Pérez",
            especialidad="Matemática",
            correo="martin@test.com",
            telefono="222222",
            estado=True
        )

        # -----------------------------------------
        # Materia y horario
        # -----------------------------------------

        self.materia = Materia.objects.create(
            nombre="Matemática",
            estado=True
        )

        self.horario = Horario.objects.create(
            dia_semana="MARTES",
            hora_inicio="09:00",
            hora_fin="10:00"
        )

        # -----------------------------------------
        # Dictado
        # -----------------------------------------

        self.dictado = DictadoMateria.objects.create(
            materia=self.materia,
            profesor=self.profesor,
            curso=self.curso,
            horario=self.horario
        )

        # -----------------------------------------
        # Alumnos
        # -----------------------------------------

        self.alumno1 = Alumno.objects.create(
            dni="63333333",
            legajo="ALUN001",
            nombre="Juan",
            apellido="López",
            fecha_nacimiento="2011-01-10",
            domicilio="Calle 1",
            telefono="333333",
            correo="juan.notas@test.com",
            curso=self.curso,
            estado=True
        )

        self.alumno2 = Alumno.objects.create(
            dni="64444444",
            legajo="ALUN002",
            nombre="María",
            apellido="Fernández",
            fecha_nacimiento="2011-02-15",
            domicilio="Calle 2",
            telefono="444444",
            correo="maria.notas@test.com",
            curso=self.curso,
            estado=True
        )

        self.alumno_otro_curso = (
            Alumno.objects.create(
                dni="65555555",
                legajo="ALUN003",
                nombre="Pedro",
                apellido="Martínez",
                fecha_nacimiento="2011-03-20",
                domicilio="Calle 3",
                telefono="555555",
                correo="pedro.notas@test.com",
                curso=self.otro_curso,
                estado=True
            )
        )

        self.fecha = (
            timezone.localdate()
            - timedelta(days=1)
        )

        self.periodo = "1° Trimestre"
        self.evaluacion = "Trabajo práctico N°1"


    def test_registra_notas_correctamente(self):

        notas = registrar_notas(
            profesor=self.profesor,
            dictado=self.dictado,
            periodo=self.periodo,
            evaluacion=self.evaluacion,
            fecha=self.fecha,
            registros=[
                {
                    "alumno": self.alumno1,
                    "calificacion": "8.50",
                    "observaciones": "Buen trabajo"
                },
                {
                    "alumno": self.alumno2,
                    "calificacion": "7",
                    "observaciones": ""
                },
            ]
        )

        self.assertEqual(
            len(notas),
            2
        )

        self.assertEqual(
            Nota.objects.count(),
            2
        )

        nota = Nota.objects.get(
            alumno=self.alumno1,
            dictado=self.dictado,
            periodo=self.periodo,
            evaluacion=self.evaluacion
        )

        self.assertEqual(
            nota.calificacion,
            Decimal("8.50")
        )


    def test_actualiza_nota_sin_duplicar(self):

        registrar_notas(
            profesor=self.profesor,
            dictado=self.dictado,
            periodo=self.periodo,
            evaluacion=self.evaluacion,
            fecha=self.fecha,
            registros=[
                {
                    "alumno": self.alumno1,
                    "calificacion": "8",
                    "observaciones": ""
                }
            ]
        )

        registrar_notas(
            profesor=self.profesor,
            dictado=self.dictado,
            periodo=self.periodo,
            evaluacion=self.evaluacion,
            fecha=self.fecha,
            registros=[
                {
                    "alumno": self.alumno1,
                    "calificacion": "9.25",
                    "observaciones": "Nota corregida"
                }
            ]
        )

        self.assertEqual(
            Nota.objects.filter(
                alumno=self.alumno1,
                dictado=self.dictado,
                periodo=self.periodo,
                evaluacion=self.evaluacion
            ).count(),
            1
        )

        nota = Nota.objects.get(
            alumno=self.alumno1,
            dictado=self.dictado,
            periodo=self.periodo,
            evaluacion=self.evaluacion
        )

        self.assertEqual(
            nota.calificacion,
            Decimal("9.25")
        )

        self.assertEqual(
            nota.observaciones,
            "Nota corregida"
        )


    def test_no_permite_calificacion_fuera_de_rango(self):

        with self.assertRaises(
            ValidationError
        ):

            registrar_notas(
                profesor=self.profesor,
                dictado=self.dictado,
                periodo=self.periodo,
                evaluacion=self.evaluacion,
                fecha=self.fecha,
                registros=[
                    {
                        "alumno": self.alumno1,
                        "calificacion": "15",
                        "observaciones": ""
                    }
                ]
            )

        self.assertFalse(
            Nota.objects.exists()
        )


    def test_no_permite_fecha_futura(self):

        fecha_futura = (
            timezone.localdate()
            + timedelta(days=1)
        )

        with self.assertRaises(
            ValidationError
        ):

            registrar_notas(
                profesor=self.profesor,
                dictado=self.dictado,
                periodo=self.periodo,
                evaluacion=self.evaluacion,
                fecha=fecha_futura,
                registros=[
                    {
                        "alumno": self.alumno1,
                        "calificacion": "8",
                        "observaciones": ""
                    }
                ]
            )

        self.assertFalse(
            Nota.objects.exists()
        )


    def test_no_permite_profesor_de_otro_dictado(self):

        with self.assertRaises(
            ValidationError
        ):

            registrar_notas(
                profesor=self.otro_profesor,
                dictado=self.dictado,
                periodo=self.periodo,
                evaluacion=self.evaluacion,
                fecha=self.fecha,
                registros=[
                    {
                        "alumno": self.alumno1,
                        "calificacion": "8",
                        "observaciones": ""
                    }
                ]
            )

        self.assertFalse(
            Nota.objects.exists()
        )


    def test_no_permite_alumno_de_otro_curso(self):

        with self.assertRaises(
            ValidationError
        ):

            registrar_notas(
                profesor=self.profesor,
                dictado=self.dictado,
                periodo=self.periodo,
                evaluacion=self.evaluacion,
                fecha=self.fecha,
                registros=[
                    {
                        "alumno": (
                            self.alumno_otro_curso
                        ),
                        "calificacion": "8",
                        "observaciones": ""
                    }
                ]
            )

        self.assertFalse(
            Nota.objects.exists()
        )


    def test_restriccion_impide_nota_duplicada(self):

        Nota.objects.create(
            alumno=self.alumno1,
            dictado=self.dictado,
            periodo=self.periodo,
            evaluacion=self.evaluacion,
            calificacion=Decimal("8"),
            fecha=self.fecha
        )

        with self.assertRaises(
            IntegrityError
        ), transaction.atomic():

            Nota.objects.create(
                alumno=self.alumno1,
                dictado=self.dictado,
                periodo=self.periodo,
                evaluacion=self.evaluacion,
                calificacion=Decimal("9"),
                fecha=self.fecha
            )


    def test_docente_registra_notas_desde_interfaz(self):

        self.client.force_login(
            self.usuario_docente
        )

        response = self.client.post(
            reverse(
                "nota_registrar",
                args=[
                    self.dictado.id_dictado
                ]
            ),
            {
                "periodo": self.periodo,
                "evaluacion": self.evaluacion,
                "fecha": self.fecha.isoformat(),

                (
                    f"calificacion_"
                    f"{self.alumno1.id_alumno}"
                ): "8.50",

                (
                    f"observaciones_"
                    f"{self.alumno1.id_alumno}"
                ): "Buen trabajo",

                # Alumno 2 queda sin nota
                (
                    f"calificacion_"
                    f"{self.alumno2.id_alumno}"
                ): "",

                (
                    f"observaciones_"
                    f"{self.alumno2.id_alumno}"
                ): "",
            }
        )

        self.assertEqual(
            response.status_code,
            302
        )

        self.assertEqual(
            Nota.objects.count(),
            1
        )

        nota = Nota.objects.get(
            alumno=self.alumno1
        )

        self.assertEqual(
            nota.calificacion,
            Decimal("8.50")
        )

        self.assertFalse(
            Nota.objects.filter(
                alumno=self.alumno2
            ).exists()
        )


    def test_docente_no_accede_dictado_ajeno(self):

        self.client.force_login(
            self.usuario_otro_docente
        )

        response = self.client.get(
            reverse(
                "nota_registrar",
                args=[
                    self.dictado.id_dictado
                ]
            )
        )

        self.assertEqual(
            response.status_code,
            404
        )

        response_historial = self.client.get(
            reverse(
                "nota_historial",
                args=[
                    self.dictado.id_dictado
                ]
            )
        )

        self.assertEqual(
            response_historial.status_code,
            404
        )


    def test_historial_agrupa_evaluacion(self):

        registrar_notas(
            profesor=self.profesor,
            dictado=self.dictado,
            periodo=self.periodo,
            evaluacion=self.evaluacion,
            fecha=self.fecha,
            registros=[
                {
                    "alumno": self.alumno1,
                    "calificacion": "8",
                    "observaciones": ""
                },
                {
                    "alumno": self.alumno2,
                    "calificacion": "7",
                    "observaciones": ""
                },
            ]
        )

        self.client.force_login(
            self.usuario_docente
        )

        response = self.client.get(
            reverse(
                "nota_historial",
                args=[
                    self.dictado.id_dictado
                ]
            )
        )

        self.assertEqual(
            response.status_code,
            200
        )

        historial = list(
            response.context[
                "historial"
            ]
        )

        self.assertEqual(
            len(historial),
            1
        )

        fila = historial[0]

        self.assertEqual(
            fila["periodo"],
            self.periodo
        )

        self.assertEqual(
            fila["evaluacion"],
            self.evaluacion
        )

        self.assertEqual(
            fila["cantidad_notas"],
            2
        )

        self.assertEqual(
            fila["fecha"],
            self.fecha
        )

class AlumnoAcademicoTestCase(TestCase):

    def setUp(self):

        # -----------------------------------------
        # Usuario alumno
        # -----------------------------------------

        self.usuario_alumno = (
            User.objects.create_user(
                username="alumno_academico",
                password="123456"
            )
        )

        PerfilUsuario.objects.create(
            usuario=self.usuario_alumno,
            rol=PerfilUsuario.Rol.ALUMNO
        )

        # -----------------------------------------
        # Usuario docente
        # -----------------------------------------

        self.usuario_docente = (
            User.objects.create_user(
                username="docente_academico",
                password="123456"
            )
        )

        PerfilUsuario.objects.create(
            usuario=self.usuario_docente,
            rol=PerfilUsuario.Rol.DOCENTE
        )

        # -----------------------------------------
        # Nivel y curso
        # -----------------------------------------

        self.nivel = NivelEducativo.objects.create(
            nombre="Secundario",
            estado=True
        )

        self.curso = Curso.objects.create(
            nombre="4°",
            division="A",
            turno="MANANA",
            nivel=self.nivel,
            estado=True
        )

        # -----------------------------------------
        # Profesor
        # -----------------------------------------

        self.profesor = Profesor.objects.create(
            usuario=self.usuario_docente,
            dni="71111111",
            legajo="PROFA001",
            nombre="Carlos",
            apellido="Gómez",
            especialidad="Historia",
            correo="carlos.academico@test.com",
            telefono="111111",
            estado=True
        )

        # -----------------------------------------
        # Materia y horario
        # -----------------------------------------

        self.materia = Materia.objects.create(
            nombre="Historia",
            estado=True
        )

        self.horario = Horario.objects.create(
            dia_semana="MIERCOLES",
            hora_inicio="10:00",
            hora_fin="11:00"
        )

        self.dictado = DictadoMateria.objects.create(
            materia=self.materia,
            profesor=self.profesor,
            curso=self.curso,
            horario=self.horario
        )

        # -----------------------------------------
        # Alumno autenticado
        # -----------------------------------------

        self.alumno = Alumno.objects.create(
            usuario=self.usuario_alumno,
            dni="72222222",
            legajo="ALUA001",
            nombre="Luciano",
            apellido="Castillo",
            fecha_nacimiento="2011-01-10",
            domicilio="Calle 1",
            telefono="222222",
            correo="luciano@test.com",
            curso=self.curso,
            estado=True
        )

        # -----------------------------------------
        # Otro alumno del mismo curso
        # -----------------------------------------

        self.otro_alumno = Alumno.objects.create(
            dni="73333333",
            legajo="ALUA002",
            nombre="Otro",
            apellido="Alumno",
            fecha_nacimiento="2011-02-15",
            domicilio="Calle 2",
            telefono="333333",
            correo="otro@test.com",
            curso=self.curso,
            estado=True
        )

        self.fecha = (
            timezone.localdate()
            - timedelta(days=1)
        )

        # -----------------------------------------
        # Nota del alumno autenticado
        # -----------------------------------------

        self.nota = Nota.objects.create(
            alumno=self.alumno,
            dictado=self.dictado,
            periodo="1° Trimestre",
            evaluacion="Parcial N°1",
            calificacion=Decimal("8.50"),
            fecha=self.fecha,
            observaciones="Buen trabajo"
        )

        # -----------------------------------------
        # Nota de otro alumno
        # -----------------------------------------

        Nota.objects.create(
            alumno=self.otro_alumno,
            dictado=self.dictado,
            periodo="1° Trimestre",
            evaluacion="Parcial N°1",
            calificacion=Decimal("4.25"),
            fecha=self.fecha,
            observaciones="PRIVADO_OTRO_ALUMNO"
        )

        # -----------------------------------------
        # Asistencias del alumno
        # -----------------------------------------

        Asistencia.objects.create(
            alumno=self.alumno,
            dictado=self.dictado,
            fecha=self.fecha,
            estado="PRESENTE"
        )

        Asistencia.objects.create(
            alumno=self.alumno,
            dictado=self.dictado,
            fecha=(
                self.fecha
                - timedelta(days=1)
            ),
            estado="AUSENTE",
            observaciones="Sin justificar"
        )

        # -----------------------------------------
        # Asistencia de otro alumno
        # -----------------------------------------

        Asistencia.objects.create(
            alumno=self.otro_alumno,
            dictado=self.dictado,
            fecha=self.fecha,
            estado="TARDE",
            observaciones="PRIVADO_ASISTENCIA_OTRO"
        )


    def test_alumno_accede_a_su_informacion_academica(self):

        self.client.force_login(
            self.usuario_alumno
        )

        response = self.client.get(
            reverse(
                "alumno_academico"
            )
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.context["alumno"],
            self.alumno
        )

        materias = response.context[
            "materias"
        ]

        self.assertEqual(
            len(materias),
            1
        )

        self.assertEqual(
            materias[0]["dictado"],
            self.dictado
        )


    def test_alumno_ve_sus_notas_y_asistencias(self):

        self.client.force_login(
            self.usuario_alumno
        )

        response = self.client.get(
            reverse(
                "alumno_academico"
            )
        )

        materia = response.context[
            "materias"
        ][0]

        notas = list(
            materia["notas"]
        )

        asistencias = list(
            materia["asistencias"]
        )

        self.assertEqual(
            len(notas),
            1
        )

        self.assertEqual(
            notas[0].alumno,
            self.alumno
        )

        self.assertEqual(
            notas[0].calificacion,
            Decimal("8.50")
        )

        self.assertEqual(
            len(asistencias),
            2
        )

        self.assertTrue(
            all(
                asistencia.alumno
                == self.alumno
                for asistencia
                in asistencias
            )
        )

        resumen = materia[
            "resumen_asistencia"
        ]

        self.assertEqual(
            resumen["total"],
            2
        )

        self.assertEqual(
            resumen["presentes"],
            1
        )

        self.assertEqual(
            resumen["ausentes"],
            1
        )

        self.assertEqual(
            resumen["tardes"],
            0
        )

        self.assertEqual(
            resumen["justificados"],
            0
        )


    def test_alumno_no_ve_datos_de_otro_alumno(self):

        self.client.force_login(
            self.usuario_alumno
        )

        response = self.client.get(
            reverse(
                "alumno_academico"
            )
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertNotContains(
            response,
            "PRIVADO_OTRO_ALUMNO"
        )

        self.assertNotContains(
            response,
            "PRIVADO_ASISTENCIA_OTRO"
        )

        self.assertNotContains(
            response,
            "4.25"
        )


    def test_docente_no_puede_acceder_vista_alumno(self):

        self.client.force_login(
            self.usuario_docente
        )

        response = self.client.get(
            reverse(
                "alumno_academico"
            )
        )

        self.assertEqual(
            response.status_code,
            302
        )

        self.assertEqual(
            response.url,
            reverse(
                "inicio_por_rol"
            )
        )


    def test_usuario_no_autenticado_es_redirigido(self):

        response = self.client.get(
            reverse(
                "alumno_academico"
            )
        )

        self.assertEqual(
            response.status_code,
            302
        )

        self.assertEqual(
            response.url,
            reverse(
                "login"
            )
        )

class TutorAcademicoTestCase(TestCase):

    def setUp(self):

        # -----------------------------------------
        # Usuario tutor
        # -----------------------------------------

        self.usuario_tutor = (
            User.objects.create_user(
                username="tutor_academico",
                password="123456"
            )
        )

        PerfilUsuario.objects.create(
            usuario=self.usuario_tutor,
            rol=PerfilUsuario.Rol.TUTOR
        )

        self.tutor = Tutor.objects.create(
            usuario=self.usuario_tutor,
            dni="81111111",
            nombre="María",
            apellido="González",
            domicilio="Calle Tutor 1",
            telefono="111111",
            correo="tutor@test.com",
            estado=True
        )

        # -----------------------------------------
        # Usuario docente
        # -----------------------------------------

        self.usuario_docente = (
            User.objects.create_user(
                username="docente_tutor_test",
                password="123456"
            )
        )

        PerfilUsuario.objects.create(
            usuario=self.usuario_docente,
            rol=PerfilUsuario.Rol.DOCENTE
        )

        # -----------------------------------------
        # Nivel y curso
        # -----------------------------------------

        self.nivel = NivelEducativo.objects.create(
            nombre="Secundario",
            estado=True
        )

        self.curso = Curso.objects.create(
            nombre="5°",
            division="A",
            turno="MANANA",
            nivel=self.nivel,
            estado=True
        )

        # -----------------------------------------
        # Profesor
        # -----------------------------------------

        self.profesor = Profesor.objects.create(
            usuario=self.usuario_docente,
            dni="82222222",
            legajo="PROFT001",
            nombre="Ana",
            apellido="Pérez",
            especialidad="Lengua",
            correo="profesor.tutor@test.com",
            telefono="222222",
            estado=True
        )

        # -----------------------------------------
        # Materia y horario
        # -----------------------------------------

        self.materia = Materia.objects.create(
            nombre="Lengua",
            estado=True
        )

        self.horario = Horario.objects.create(
            dia_semana="JUEVES",
            hora_inicio="08:00",
            hora_fin="09:00"
        )

        self.dictado = DictadoMateria.objects.create(
            materia=self.materia,
            profesor=self.profesor,
            curso=self.curso,
            horario=self.horario
        )

        # -----------------------------------------
        # Alumno asociado al tutor
        # -----------------------------------------

        self.alumno = Alumno.objects.create(
            dni="83333333",
            legajo="ALUT001",
            nombre="Juan",
            apellido="Gómez",
            fecha_nacimiento="2010-01-10",
            domicilio="Calle Alumno 1",
            telefono="333333",
            correo="juan.tutor@test.com",
            curso=self.curso,
            estado=True
        )

        TutorAlumno.objects.create(
            tutor=self.tutor,
            alumno=self.alumno
        )

        # -----------------------------------------
        # Alumno NO asociado al tutor
        # -----------------------------------------

        self.otro_alumno = Alumno.objects.create(
            dni="84444444",
            legajo="ALUT002",
            nombre="Pedro",
            apellido="Martínez",
            fecha_nacimiento="2010-02-15",
            domicilio="Calle Alumno 2",
            telefono="444444",
            correo="pedro.tutor@test.com",
            curso=self.curso,
            estado=True
        )

        self.fecha = (
            timezone.localdate()
            - timedelta(days=1)
        )

        # -----------------------------------------
        # Nota del alumno asociado
        # -----------------------------------------

        Nota.objects.create(
            alumno=self.alumno,
            dictado=self.dictado,
            periodo="1° Trimestre",
            evaluacion="Parcial N°1",
            calificacion=Decimal("9.00"),
            fecha=self.fecha,
            observaciones="NOTA_HIJO_ASOCIADO"
        )

        # -----------------------------------------
        # Nota del alumno NO asociado
        # -----------------------------------------

        Nota.objects.create(
            alumno=self.otro_alumno,
            dictado=self.dictado,
            periodo="1° Trimestre",
            evaluacion="Parcial N°1",
            calificacion=Decimal("4.00"),
            fecha=self.fecha,
            observaciones="NOTA_PRIVADA_OTRO_ALUMNO"
        )

        # -----------------------------------------
        # Asistencias del alumno asociado
        # -----------------------------------------

        Asistencia.objects.create(
            alumno=self.alumno,
            dictado=self.dictado,
            fecha=self.fecha,
            estado="PRESENTE"
        )

        Asistencia.objects.create(
            alumno=self.alumno,
            dictado=self.dictado,
            fecha=(
                self.fecha
                - timedelta(days=1)
            ),
            estado="JUSTIFICADO",
            observaciones="Falta justificada"
        )

        # -----------------------------------------
        # Asistencia del alumno NO asociado
        # -----------------------------------------

        Asistencia.objects.create(
            alumno=self.otro_alumno,
            dictado=self.dictado,
            fecha=self.fecha,
            estado="AUSENTE",
            observaciones="ASISTENCIA_PRIVADA_OTRO"
        )


    def test_tutor_ve_sus_alumnos_asociados(self):

        self.client.force_login(
            self.usuario_tutor
        )

        response = self.client.get(
            reverse(
                "tutor_mis_hijos"
            )
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertContains(
            response,
            self.alumno.nombre
        )

        self.assertNotContains(
            response,
            self.otro_alumno.nombre
        )


    def test_tutor_accede_al_detalle_de_alumno_asociado(self):

        self.client.force_login(
            self.usuario_tutor
        )

        response = self.client.get(
            reverse(
                "tutor_detalle_alumno",
                args=[
                    self.alumno.id_alumno
                ]
            )
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.context["alumno"],
            self.alumno
        )


    def test_tutor_ve_notas_y_asistencias_del_alumno(self):

        self.client.force_login(
            self.usuario_tutor
        )

        response = self.client.get(
            reverse(
                "tutor_detalle_alumno",
                args=[
                    self.alumno.id_alumno
                ]
            )
        )

        materias = response.context[
            "materias"
        ]

        self.assertEqual(
            len(materias),
            1
        )

        materia = materias[0]

        notas = list(
            materia["notas"]
        )

        asistencias = list(
            materia["asistencias"]
        )

        self.assertEqual(
            len(notas),
            1
        )

        self.assertEqual(
            notas[0].calificacion,
            Decimal("9.00")
        )

        self.assertEqual(
            notas[0].alumno,
            self.alumno
        )

        self.assertEqual(
            len(asistencias),
            2
        )

        self.assertTrue(
            all(
                asistencia.alumno
                == self.alumno
                for asistencia
                in asistencias
            )
        )

        resumen = materia[
            "resumen_asistencia"
        ]

        self.assertEqual(
            resumen["total"],
            2
        )

        self.assertEqual(
            resumen["presentes"],
            1
        )

        self.assertEqual(
            resumen["ausentes"],
            0
        )

        self.assertEqual(
            resumen["tardes"],
            0
        )

        self.assertEqual(
            resumen["justificados"],
            1
        )


    def test_tutor_no_ve_informacion_de_otro_alumno(self):

        self.client.force_login(
            self.usuario_tutor
        )

        response = self.client.get(
            reverse(
                "tutor_detalle_alumno",
                args=[
                    self.alumno.id_alumno
                ]
            )
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertNotContains(
            response,
            "NOTA_PRIVADA_OTRO_ALUMNO"
        )

        self.assertNotContains(
            response,
            "ASISTENCIA_PRIVADA_OTRO"
        )

        self.assertNotContains(
            response,
            "4.00"
        )


    def test_tutor_no_puede_acceder_alumno_no_asociado(self):

        self.client.force_login(
            self.usuario_tutor
        )

        response = self.client.get(
            reverse(
                "tutor_detalle_alumno",
                args=[
                    self.otro_alumno.id_alumno
                ]
            )
        )

        self.assertEqual(
            response.status_code,
            404
        )


    def test_otro_rol_no_puede_acceder_vista_tutor(self):

        self.client.force_login(
            self.usuario_docente
        )

        response = self.client.get(
            reverse(
                "tutor_mis_hijos"
            )
        )

        self.assertEqual(
            response.status_code,
            302
        )

        self.assertEqual(
            response.url,
            reverse(
                "inicio_por_rol"
            )
        )