from datetime import date, time
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from academic.models import (
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
from accounts.models import PerfilUsuario
from billing.models import CuotaMensual, Factura
from billing.services import generar_factura_alumno
from services.models import (
    ContratacionComedor,
    ContratacionTransporte,
    RutaTransporte,
    ServicioComedor,
)
from sports.models import (
    Deporte,
    GrupoDeportivo,
    InscripcionDeporte,
)


class Command(BaseCommand):
    help = "Carga datos demo para probar el sistema completo."

    def crear_usuario(
        self,
        username,
        password,
        rol,
        email,
        *,
        is_staff=False,
        is_superuser=False,
    ):
        usuario, creado = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_active": True,
                "is_staff": is_staff,
                "is_superuser": is_superuser,
            },
        )

        usuario.email = email
        usuario.is_active = True
        usuario.is_staff = is_staff
        usuario.is_superuser = is_superuser

        if creado:
            usuario.set_password(password)

        usuario.save()

        PerfilUsuario.objects.update_or_create(
            usuario=usuario,
            defaults={
                "rol": rol,
                "debe_cambiar_password": False,
            },
        )

        return usuario, creado

    @transaction.atomic
    def handle(self, *args, **options):
        credenciales_nuevas = []

        # -------------------------------------------------
        # ADMINISTRADOR
        # -------------------------------------------------

        admin, creado = self.crear_usuario(
            "admin_demo",
            "AdminDemo2026!",
            PerfilUsuario.Rol.ADMIN,
            "admin.demo@educar.test",
            is_staff=True,
            is_superuser=True,
        )

        if creado:
            credenciales_nuevas.append(
                ("ADMIN", "admin_demo", "AdminDemo2026!")
            )

        # -------------------------------------------------
        # NIVELES Y CURSOS
        # -------------------------------------------------

        primario, _ = NivelEducativo.objects.update_or_create(
            nombre="Primario",
            defaults={"estado": True},
        )

        secundario, _ = NivelEducativo.objects.update_or_create(
            nombre="Secundario",
            defaults={"estado": True},
        )

        quinto_a, _ = Curso.objects.get_or_create(
            nombre="5to",
            division="A",
            turno="MANANA",
            nivel=primario,
            defaults={"estado": True},
        )

        segundo_a, _ = Curso.objects.get_or_create(
            nombre="2do",
            division="A",
            turno="MANANA",
            nivel=secundario,
            defaults={"estado": True},
        )

        # -------------------------------------------------
        # PROFESORES
        # -------------------------------------------------

        profesores_datos = [
            {
                "username": "prof.matematica",
                "dni": "99000101",
                "legajo": "DEMOP001",
                "nombre": "Laura",
                "apellido": "Gómez",
                "especialidad": "Matemática",
                "correo": "laura.gomez@educar.test",
                "telefono": "3624001001",
            },
            {
                "username": "prof.lengua",
                "dni": "99000102",
                "legajo": "DEMOP002",
                "nombre": "Martín",
                "apellido": "López",
                "especialidad": "Lengua",
                "correo": "martin.lopez@educar.test",
                "telefono": "3624001002",
            },
            {
                "username": "prof.deportes",
                "dni": "99000103",
                "legajo": "DEMOP003",
                "nombre": "Carla",
                "apellido": "Benítez",
                "especialidad": "Educación Física",
                "correo": "carla.benitez@educar.test",
                "telefono": "3624001003",
            },
        ]

        profesores = {}

        for datos in profesores_datos:
            usuario, creado = self.crear_usuario(
                datos["username"],
                "DocenteDemo2026!",
                PerfilUsuario.Rol.DOCENTE,
                datos["correo"],
            )

            if creado:
                credenciales_nuevas.append(
                    (
                        "DOCENTE",
                        datos["username"],
                        "DocenteDemo2026!",
                    )
                )

            profesor, _ = Profesor.objects.update_or_create(
                dni=datos["dni"],
                defaults={
                    "usuario": usuario,
                    "legajo": datos["legajo"],
                    "nombre": datos["nombre"],
                    "apellido": datos["apellido"],
                    "especialidad": datos["especialidad"],
                    "correo": datos["correo"],
                    "telefono": datos["telefono"],
                    "estado": True,
                },
            )

            profesores[datos["username"]] = profesor

        # -------------------------------------------------
        # TUTORES
        # -------------------------------------------------

        tutores_datos = [
            {
                "clave": "perez",
                "username": "tutor.perez",
                "dni": "99000201",
                "nombre": "Juan",
                "apellido": "Pérez",
                "domicilio": "Av. Sarmiento 1200",
                "telefono": "3624111001",
                "correo": "juan.perez@educar.test",
            },
            {
                "clave": "gomez",
                "username": "tutor.gomez",
                "dni": "99000202",
                "nombre": "María",
                "apellido": "Gómez",
                "domicilio": "Calle Córdoba 450",
                "telefono": "3624111002",
                "correo": "maria.gomez@educar.test",
            },
            {
                "clave": "romero",
                "username": "tutor.romero",
                "dni": "99000203",
                "nombre": "Lucía",
                "apellido": "Romero",
                "domicilio": "Av. Alberdi 830",
                "telefono": "3624111003",
                "correo": "lucia.romero@educar.test",
            },
        ]

        tutores = {}

        for datos in tutores_datos:
            usuario, creado = self.crear_usuario(
                datos["username"],
                "TutorDemo2026!",
                PerfilUsuario.Rol.TUTOR,
                datos["correo"],
            )

            if creado:
                credenciales_nuevas.append(
                    (
                        "TUTOR",
                        datos["username"],
                        "TutorDemo2026!",
                    )
                )

            tutor, _ = Tutor.objects.update_or_create(
                dni=datos["dni"],
                defaults={
                    "usuario": usuario,
                    "nombre": datos["nombre"],
                    "apellido": datos["apellido"],
                    "domicilio": datos["domicilio"],
                    "telefono": datos["telefono"],
                    "correo": datos["correo"],
                    "estado": True,
                },
            )

            tutores[datos["clave"]] = tutor

        # -------------------------------------------------
        # ALUMNOS
        # -------------------------------------------------

        alumnos_datos = [
            {
                "clave": "sofia",
                "username": "alumno.sofia",
                "dni": "99000301",
                "legajo": "DEMOA001",
                "nombre": "Sofía",
                "apellido": "Pérez",
                "fecha": date(2015, 4, 12),
                "curso": quinto_a,
                "tutor": "perez",
            },
            {
                "clave": "mateo",
                "username": "alumno.mateo",
                "dni": "99000302",
                "legajo": "DEMOA002",
                "nombre": "Mateo",
                "apellido": "Pérez",
                "fecha": date(2015, 7, 3),
                "curso": quinto_a,
                "tutor": "perez",
            },
            {
                "clave": "valentina",
                "username": "alumno.valentina",
                "dni": "99000303",
                "legajo": "DEMOA003",
                "nombre": "Valentina",
                "apellido": "Gómez",
                "fecha": date(2015, 2, 18),
                "curso": quinto_a,
                "tutor": "gomez",
            },
            {
                "clave": "tomas",
                "username": "alumno.tomas",
                "dni": "99000304",
                "legajo": "DEMOA004",
                "nombre": "Tomás",
                "apellido": "Romero",
                "fecha": date(2012, 8, 25),
                "curso": segundo_a,
                "tutor": "romero",
            },
            {
                "clave": "martina",
                "username": "alumno.martina",
                "dni": "99000305",
                "legajo": "DEMOA005",
                "nombre": "Martina",
                "apellido": "Romero",
                "fecha": date(2012, 11, 10),
                "curso": segundo_a,
                "tutor": "romero",
            },
        ]

        alumnos = {}

        for datos in alumnos_datos:
            correo = (
                f"{datos['username'].replace('.', '_')}"
                "@educar.test"
            )

            usuario, creado = self.crear_usuario(
                datos["username"],
                "AlumnoDemo2026!",
                PerfilUsuario.Rol.ALUMNO,
                correo,
            )

            if creado:
                credenciales_nuevas.append(
                    (
                        "ALUMNO",
                        datos["username"],
                        "AlumnoDemo2026!",
                    )
                )

            alumno, _ = Alumno.objects.update_or_create(
                dni=datos["dni"],
                defaults={
                    "usuario": usuario,
                    "legajo": datos["legajo"],
                    "nombre": datos["nombre"],
                    "apellido": datos["apellido"],
                    "fecha_nacimiento": datos["fecha"],
                    "domicilio": "Domicilio de prueba",
                    "telefono": "3624222000",
                    "correo": correo,
                    "curso": datos["curso"],
                    "estado": True,
                },
            )

            TutorAlumno.objects.get_or_create(
                tutor=tutores[datos["tutor"]],
                alumno=alumno,
            )

            alumnos[datos["clave"]] = alumno

        # -------------------------------------------------
        # MATERIAS Y HORARIOS
        # -------------------------------------------------

        matematica, _ = Materia.objects.update_or_create(
            nombre="Matemática",
            defaults={"estado": True},
        )

        lengua, _ = Materia.objects.update_or_create(
            nombre="Lengua",
            defaults={"estado": True},
        )

        ciencias, _ = Materia.objects.update_or_create(
            nombre="Ciencias Naturales",
            defaults={"estado": True},
        )

        lunes_8, _ = Horario.objects.get_or_create(
            dia_semana="LUNES",
            hora_inicio=time(8, 0),
            hora_fin=time(9, 0),
        )

        martes_9, _ = Horario.objects.get_or_create(
            dia_semana="MARTES",
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0),
        )

        miercoles_10, _ = Horario.objects.get_or_create(
            dia_semana="MIERCOLES",
            hora_inicio=time(10, 0),
            hora_fin=time(11, 0),
        )

        dictado_mate_primario, _ = DictadoMateria.objects.get_or_create(
            materia=matematica,
            profesor=profesores["prof.matematica"],
            curso=quinto_a,
            horario=lunes_8,
        )

        DictadoMateria.objects.get_or_create(
            materia=lengua,
            profesor=profesores["prof.lengua"],
            curso=quinto_a,
            horario=martes_9,
        )

        DictadoMateria.objects.get_or_create(
            materia=ciencias,
            profesor=profesores["prof.matematica"],
            curso=quinto_a,
            horario=miercoles_10,
        )

        dictado_mate_secundario, _ = (
            DictadoMateria.objects.get_or_create(
                materia=matematica,
                profesor=profesores["prof.matematica"],
                curso=segundo_a,
                horario=lunes_8,
            )
        )

        DictadoMateria.objects.get_or_create(
            materia=lengua,
            profesor=profesores["prof.lengua"],
            curso=segundo_a,
            horario=martes_9,
        )

        # -------------------------------------------------
        # ASISTENCIAS Y NOTAS
        # -------------------------------------------------

        calificaciones = {
            "sofia": Decimal("9.00"),
            "mateo": Decimal("8.00"),
            "valentina": Decimal("9.50"),
            "tomas": Decimal("7.50"),
            "martina": Decimal("8.50"),
        }

        for clave, alumno in alumnos.items():
            if alumno.curso_id == quinto_a.id_curso:
                dictado = dictado_mate_primario
            else:
                dictado = dictado_mate_secundario

            Asistencia.objects.update_or_create(
                alumno=alumno,
                dictado=dictado,
                fecha=date(2026, 11, 3),
                defaults={
                    "estado": "PRESENTE",
                    "observaciones": "",
                },
            )

            Nota.objects.update_or_create(
                alumno=alumno,
                dictado=dictado,
                periodo="Tercer trimestre",
                evaluacion="Evaluación integradora",
                defaults={
                    "calificacion": calificaciones[clave],
                    "fecha": date(2026, 11, 4),
                    "observaciones": "Dato de demostración",
                },
            )

        # -------------------------------------------------
        # DEPORTES
        # -------------------------------------------------

        futbol, _ = Deporte.objects.update_or_create(
            nombre="Fútbol",
            defaults={
                "descripcion": "Entrenamiento recreativo de fútbol",
                "valor_mensual": Decimal("12000.00"),
                "estado": True,
            },
        )

        voley, _ = Deporte.objects.update_or_create(
            nombre="Vóley",
            defaults={
                "descripcion": "Entrenamiento recreativo de vóley",
                "valor_mensual": Decimal("10000.00"),
                "estado": True,
            },
        )

        basquet, _ = Deporte.objects.update_or_create(
            nombre="Básquet",
            defaults={
                "descripcion": "Entrenamiento recreativo de básquet",
                "valor_mensual": Decimal("11000.00"),
                "estado": True,
            },
        )

        lunes_16, _ = Horario.objects.get_or_create(
            dia_semana="LUNES",
            hora_inicio=time(16, 0),
            hora_fin=time(17, 0),
        )

        miercoles_16, _ = Horario.objects.get_or_create(
            dia_semana="MIERCOLES",
            hora_inicio=time(16, 0),
            hora_fin=time(17, 0),
        )

        viernes_16, _ = Horario.objects.get_or_create(
            dia_semana="VIERNES",
            hora_inicio=time(16, 0),
            hora_fin=time(17, 0),
        )

        grupo_futbol, _ = GrupoDeportivo.objects.get_or_create(
            deporte=futbol,
            nivel=primario,
            profesor=profesores["prof.deportes"],
            horario=lunes_16,
            defaults={"estado": True},
        )

        grupo_basquet, _ = GrupoDeportivo.objects.get_or_create(
            deporte=basquet,
            nivel=primario,
            profesor=profesores["prof.deportes"],
            horario=miercoles_16,
            defaults={"estado": True},
        )

        grupo_voley, _ = GrupoDeportivo.objects.get_or_create(
            deporte=voley,
            nivel=secundario,
            profesor=profesores["prof.deportes"],
            horario=viernes_16,
            defaults={"estado": True},
        )

        inscripciones = [
            (alumnos["sofia"], grupo_futbol),
            (alumnos["mateo"], grupo_basquet),
            (alumnos["valentina"], grupo_futbol),
            (alumnos["valentina"], grupo_basquet),
            (alumnos["tomas"], grupo_voley),
            (alumnos["martina"], grupo_voley),
        ]

        for alumno, grupo in inscripciones:
            inscripcion, _ = (
                InscripcionDeporte.objects.get_or_create(
                    alumno=alumno,
                    grupo=grupo,
                    defaults={"estado": True},
                )
            )

            inscripcion.estado = True
            inscripcion.fecha_baja = None
            inscripcion.save(
                update_fields=[
                    "estado",
                    "fecha_baja",
                ]
            )

        # -------------------------------------------------
        # TRANSPORTE
        # -------------------------------------------------

        ruta_centro, _ = RutaTransporte.objects.update_or_create(
            nombre="Ruta Centro",
            defaults={
                "descripcion": "Recorrido zona centro",
                "valor_mensual": Decimal("9000.00"),
                "estado": True,
            },
        )

        ruta_norte, _ = RutaTransporte.objects.update_or_create(
            nombre="Ruta Norte",
            defaults={
                "descripcion": "Recorrido zona norte",
                "valor_mensual": Decimal("11000.00"),
                "estado": True,
            },
        )

        transportes = [
            ("sofia", ruta_centro, 11),
            ("mateo", ruta_centro, 11),
            ("tomas", ruta_norte, 11),
            ("sofia", ruta_centro, 12),
            ("tomas", ruta_norte, 12),
            ("martina", ruta_norte, 12),
        ]

        for clave, ruta, mes in transportes:
            ContratacionTransporte.objects.update_or_create(
                alumno=alumnos[clave],
                mes=mes,
                anio=2026,
                defaults={
                    "ruta": ruta,
                    "estado": True,
                },
            )

        # -------------------------------------------------
        # COMEDOR
        # -------------------------------------------------

        comedor, _ = ServicioComedor.objects.update_or_create(
            nombre="Comedor Jornada Completa",
            defaults={
                "descripcion": "Servicio mensual de comedor escolar",
                "valor_mensual": Decimal("15000.00"),
                "estado": True,
            },
        )

        comedor_alumnos = [
            ("sofia", 11),
            ("valentina", 11),
            ("martina", 11),
            ("sofia", 12),
            ("valentina", 12),
            ("mateo", 12),
        ]

        for clave, mes in comedor_alumnos:
            ContratacionComedor.objects.update_or_create(
                alumno=alumnos[clave],
                mes=mes,
                anio=2026,
                defaults={
                    "servicio": comedor,
                    "estado": True,
                },
            )

        # -------------------------------------------------
        # CUOTAS
        # -------------------------------------------------

        CuotaMensual.objects.update_or_create(
            mes=11,
            anio=2026,
            defaults={
                "valor": Decimal("35000.00"),
                "fecha_vencimiento": date(2026, 11, 10),
                "estado": True,
            },
        )

        CuotaMensual.objects.update_or_create(
            mes=12,
            anio=2026,
            defaults={
                "valor": Decimal("36000.00"),
                "fecha_vencimiento": date(2026, 12, 10),
                "estado": True,
            },
        )

        # -------------------------------------------------
        # FACTURAS
        # -------------------------------------------------

        facturas_creadas = 0

        for alumno in alumnos.values():
            for mes in (11, 12):
                existe = Factura.objects.filter(
                    alumno=alumno,
                    mes=mes,
                    anio=2026,
                ).exists()

                if not existe:
                    generar_factura_alumno(
                        alumno,
                        mes,
                        2026,
                    )
                    facturas_creadas += 1

        # -------------------------------------------------
        # RESULTADO
        # -------------------------------------------------

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Datos demo cargados correctamente."
            )
        )

        self.stdout.write(
            f"Alumnos: {Alumno.objects.count()}"
        )
        self.stdout.write(
            f"Tutores: {Tutor.objects.count()}"
        )
        self.stdout.write(
            f"Profesores: {Profesor.objects.count()}"
        )
        self.stdout.write(
            f"Facturas demo nuevas: {facturas_creadas}"
        )

        if credenciales_nuevas:
            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING(
                    "Credenciales creadas:"
                )
            )

            for rol, username, password in credenciales_nuevas:
                self.stdout.write(
                    f"{rol}: {username} / {password}"
                )

        self.stdout.write("")
        self.stdout.write(
            "Tutor recomendado para probar Mobile:"
        )
        self.stdout.write(
            "tutor.perez / TutorDemo2026!"
        )