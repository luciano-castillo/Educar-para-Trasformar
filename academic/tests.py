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
    NivelEducativo,
    Curso,
    Alumno,
    Profesor,
    Materia,
    Horario,
    DictadoMateria,
    Asistencia,
    Nota,
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
        ):

            with transaction.atomic():

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
        ):

            with transaction.atomic():

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