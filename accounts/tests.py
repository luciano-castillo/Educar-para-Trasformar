from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from academic.models import (
    Alumno,
    Curso,
    NivelEducativo,
    Profesor,
    Tutor,
)

from .models import PerfilUsuario


class PrimerAccesoTestCase(TestCase):

    def setUp(self):

        self.usuario = User.objects.create_user(
            username="alumno_primer_acceso",
            email="alumno@test.com",
            password="Temporal123!"
        )

        self.perfil = PerfilUsuario.objects.create(
            usuario=self.usuario,
            rol=PerfilUsuario.Rol.ALUMNO,
            debe_cambiar_password=True
        )


    def test_login_redirige_a_cambio_password(self):

        response = self.client.post(
            reverse("login"),
            {
                "perfil": "ALUMNO",
                "identificador": (
                    "alumno_primer_acceso"
                ),
                "password": "Temporal123!",
            }
        )

        self.assertRedirects(
            response,
            reverse(
                "cambiar_password_inicial"
            )
        )


    def test_inicio_por_rol_exige_cambio_password(self):

        self.client.force_login(
            self.usuario
        )

        response = self.client.get(
            reverse("inicio_por_rol")
        )

        self.assertRedirects(
            response,
            reverse(
                "cambiar_password_inicial"
            )
        )


    def test_cambia_password_correctamente(self):

        self.client.force_login(
            self.usuario
        )

        response = self.client.post(
            reverse(
                "cambiar_password_inicial"
            ),
            {
                "new_password1": (
                    "NuevaClaveSegura2026!"
                ),
                "new_password2": (
                    "NuevaClaveSegura2026!"
                ),
            }
        )

        self.assertRedirects(
            response,
            reverse("inicio_por_rol"),
            fetch_redirect_response=False
        )

        self.usuario.refresh_from_db()
        self.perfil.refresh_from_db()

        self.assertTrue(
            self.usuario.check_password(
                "NuevaClaveSegura2026!"
            )
        )

        self.assertFalse(
            self.perfil.debe_cambiar_password
        )


    def test_usuario_sin_cambio_pendiente_no_accede_a_pantalla(self):

        self.perfil.debe_cambiar_password = False
        self.perfil.save()

        self.client.force_login(
            self.usuario
        )

        response = self.client.get(
            reverse(
                "cambiar_password_inicial"
            )
        )

        self.assertRedirects(
            response,
            reverse("inicio_por_rol"),
            fetch_redirect_response=False
        )

class GestionCuentasTestCase(TestCase):

    def setUp(self):

        # -----------------------------------------
        # Administrador
        # -----------------------------------------

        self.admin = User.objects.create_user(
            username="admin_cuentas",
            password="Admin123!"
        )

        PerfilUsuario.objects.create(
            usuario=self.admin,
            rol=PerfilUsuario.Rol.ADMIN,
            debe_cambiar_password=False,
        )


        # -----------------------------------------
        # Nivel y curso
        # -----------------------------------------

        self.nivel = (
            NivelEducativo.objects.create(
                nombre="Secundario",
                estado=True,
            )
        )

        self.curso = Curso.objects.create(
            nombre="1°",
            division="A",
            turno="MANANA",
            nivel=self.nivel,
            estado=True,
        )


        # -----------------------------------------
        # Alumno
        # -----------------------------------------

        self.alumno = Alumno.objects.create(
            dni="40111222",
            legajo="ALUC001",
            nombre="Juan",
            apellido="Pérez",
            fecha_nacimiento="2012-01-10",
            domicilio="Calle 1",
            telefono="111111",
            correo="juan.cuenta@test.com",
            curso=self.curso,
            estado=True,
        )


        # -----------------------------------------
        # Profesor
        # -----------------------------------------

        self.profesor = Profesor.objects.create(
            dni="40222333",
            legajo="PROFC001",
            nombre="Laura",
            apellido="Gómez",
            especialidad="Matemática",
            correo="laura.cuenta@test.com",
            telefono="222222",
            estado=True,
        )


        # -----------------------------------------
        # Tutor
        # -----------------------------------------

        self.tutor = Tutor.objects.create(
            dni="40333444",
            nombre="Carlos",
            apellido="López",
            domicilio="Calle Tutor",
            telefono="333333",
            correo="carlos.cuenta@test.com",
            estado=True,
        )


        self.client.force_login(
            self.admin
        )


    def test_admin_crea_cuenta_alumno(self):

        response = self.client.post(
            reverse(
                "crear_cuenta_alumno",
                args=[
                    self.alumno.id_alumno
                ]
            )
        )

        self.assertEqual(
            response.status_code,
            302
        )

        self.alumno.refresh_from_db()

        self.assertIsNotNone(
            self.alumno.usuario
        )

        self.assertEqual(
            self.alumno.usuario.perfil.rol,
            PerfilUsuario.Rol.ALUMNO
        )

        self.assertTrue(
            self.alumno.usuario
            .perfil
            .debe_cambiar_password
        )


    def test_admin_crea_cuenta_profesor(self):

        self.client.post(
            reverse(
                "crear_cuenta_profesor",
                args=[
                    self.profesor.id_profesor
                ]
            )
        )

        self.profesor.refresh_from_db()

        self.assertIsNotNone(
            self.profesor.usuario
        )

        self.assertEqual(
            self.profesor.usuario.perfil.rol,
            PerfilUsuario.Rol.DOCENTE
        )


    def test_admin_crea_cuenta_tutor(self):

        self.client.post(
            reverse(
                "crear_cuenta_tutor",
                args=[
                    self.tutor.id_tutor
                ]
            )
        )

        self.tutor.refresh_from_db()

        self.assertIsNotNone(
            self.tutor.usuario
        )

        self.assertEqual(
            self.tutor.usuario.perfil.rol,
            PerfilUsuario.Rol.TUTOR
        )


    def test_no_permite_crear_dos_cuentas_misma_persona(self):

        url = reverse(
            "crear_cuenta_alumno",
            args=[
                self.alumno.id_alumno
            ]
        )

        self.client.post(url)

        cantidad_antes = (
            User.objects.count()
        )

        self.client.post(url)

        cantidad_despues = (
            User.objects.count()
        )

        self.assertEqual(
            cantidad_antes,
            cantidad_despues
        )


    def test_restablecer_password_exige_nuevo_cambio(self):

        self.client.post(
            reverse(
                "crear_cuenta_alumno",
                args=[
                    self.alumno.id_alumno
                ]
            )
        )

        self.alumno.refresh_from_db()

        perfil = (
            self.alumno.usuario.perfil
        )

        perfil.debe_cambiar_password = False
        perfil.save()

        password_anterior = (
            self.alumno.usuario.password
        )

        self.client.post(
            reverse(
                "restablecer_password_alumno",
                args=[
                    self.alumno.id_alumno
                ]
            )
        )

        self.alumno.usuario.refresh_from_db()
        perfil.refresh_from_db()

        self.assertNotEqual(
            password_anterior,
            self.alumno.usuario.password
        )

        self.assertTrue(
            perfil.debe_cambiar_password
        )


    def test_desactivar_alumno_desactiva_usuario(self):

        self.client.post(
            reverse(
                "crear_cuenta_alumno",
                args=[
                    self.alumno.id_alumno
                ]
            )
        )

        self.alumno.refresh_from_db()

        self.client.post(
            reverse(
                "alumno_desactivar",
                args=[
                    self.alumno.id_alumno
                ]
            )
        )

        self.alumno.refresh_from_db()
        self.alumno.usuario.refresh_from_db()

        self.assertFalse(
            self.alumno.estado
        )

        self.assertFalse(
            self.alumno.usuario.is_active
        )

class PermisosAdministracionTestCase(TestCase):

    def setUp(self):

        self.admin = User.objects.create_user(
            username="admin_seguridad",
            password="Admin123!",
        )

        PerfilUsuario.objects.create(
            usuario=self.admin,
            rol=PerfilUsuario.Rol.ADMIN,
            debe_cambiar_password=False,
        )

        self.usuarios_no_admin = []

        for indice, rol in enumerate(
            [
                PerfilUsuario.Rol.ALUMNO,
                PerfilUsuario.Rol.DOCENTE,
                PerfilUsuario.Rol.TUTOR,
            ],
            start=1,
        ):

            usuario = User.objects.create_user(
                username=f"usuario_seguridad_{indice}",
                password="Prueba123!",
            )

            PerfilUsuario.objects.create(
                usuario=usuario,
                rol=rol,
                debe_cambiar_password=False,
            )

            self.usuarios_no_admin.append(
                usuario
            )

        self.urls_admin = [
            reverse("admin_dashboard"),
            reverse("alumno_lista"),
            reverse("profesor_lista"),
            reverse("deporte_lista"),
            reverse("ruta_lista"),
            reverse("comedor_lista"),
            reverse("cuota_lista"),
            reverse("factura_lista"),
            reverse("reporte_pagos"),
        ]

    def test_roles_no_admin_no_acceden_a_gestion(
        self,
    ):

        for usuario in self.usuarios_no_admin:

            self.client.force_login(
                usuario
            )

            for url in self.urls_admin:

                with self.subTest(
                    usuario=usuario.username,
                    url=url,
                ):

                    response = self.client.get(
                        url
                    )

                    self.assertEqual(
                        response.status_code,
                        302,
                    )

                    self.assertEqual(
                        response.url,
                        reverse(
                            "inicio_por_rol"
                        ),
                    )

            self.client.logout()

    def test_admin_accede_a_modulos_de_gestion(
        self,
    ):

        self.client.force_login(
            self.admin
        )

        for url in self.urls_admin:

            with self.subTest(
                url=url
            ):

                response = self.client.get(
                    url
                )

                self.assertEqual(
                    response.status_code,
                    200,
                )
    
    def test_usuario_anonimo_no_accede_a_gestion(
        self,
    ):

        response = self.client.get(
            reverse(
                "factura_lista"
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertEqual(
            response.url,
            reverse(
                "login"
            ),
        )