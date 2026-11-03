from datetime import date

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from academic.models import (
    Alumno,
    Curso,
    NivelEducativo,
    Tutor,
    TutorAlumno,
)
from accounts.models import PerfilUsuario
from billing.models import (
    DetalleFactura,
    Factura,
)


class ApiTutorTest(APITestCase):
    def setUp(self):

        self.nivel = NivelEducativo.objects.create(
            nombre="Primario",
            estado=True,
        )

        self.curso = Curso.objects.create(
            nombre="5to",
            division="A",
            turno="MANANA",
            nivel=self.nivel,
            estado=True,
        )

        self.usuario_tutor = User.objects.create_user(
            username="tutor_prueba",
            password="ClaveSegura123!",
        )

        PerfilUsuario.objects.create(
            usuario=self.usuario_tutor,
            rol=PerfilUsuario.Rol.TUTOR,
            debe_cambiar_password=False,
        )

        self.tutor = Tutor.objects.create(
            usuario=self.usuario_tutor,
            dni="30111222",
            nombre="Carlos",
            apellido="Pérez",
            domicilio="Calle Principal 123",
            telefono="3624000001",
            correo="tutor@example.com",
            estado=True,
        )

        self.alumno = Alumno.objects.create(
            dni="50111222",
            legajo="A001",
            nombre="Ana",
            apellido="Pérez",
            fecha_nacimiento=date(
                2015,
                5,
                10,
            ),
            domicilio="Calle Principal 123",
            telefono="3624000002",
            correo="ana@example.com",
            curso=self.curso,
            estado=True,
        )

        TutorAlumno.objects.create(
            tutor=self.tutor,
            alumno=self.alumno,
        )

        self.factura = Factura.objects.create(
            alumno=self.alumno,
            mes=10,
            anio=2026,
            fecha_vencimiento=date(
                2026,
                10,
                10,
            ),
            estado="PENDIENTE",
        )

        DetalleFactura.objects.create(
            factura=self.factura,
            tipo_concepto="CUOTA",
            descripcion="Cuota octubre",
            importe="10000.00",
        )

        DetalleFactura.objects.create(
            factura=self.factura,
            tipo_concepto="DEPORTE",
            descripcion="Deporte",
            importe="5000.00",
        )

        self.usuario_otro_tutor = User.objects.create_user(
            username="otro_tutor",
            password="ClaveSegura456!",
        )

        PerfilUsuario.objects.create(
            usuario=self.usuario_otro_tutor,
            rol=PerfilUsuario.Rol.TUTOR,
            debe_cambiar_password=False,
        )

        self.otro_tutor = Tutor.objects.create(
            usuario=self.usuario_otro_tutor,
            dni="30999888",
            nombre="María",
            apellido="Gómez",
            domicilio="Otra calle 456",
            telefono="3624000003",
            correo="otro@example.com",
            estado=True,
        )

        self.alumno_ajeno = Alumno.objects.create(
            dni="50999888",
            legajo="A002",
            nombre="Bruno",
            apellido="Gómez",
            fecha_nacimiento=date(
                2015,
                8,
                20,
            ),
            domicilio="Otra calle 456",
            telefono="3624000004",
            correo="bruno@example.com",
            curso=self.curso,
            estado=True,
        )

        TutorAlumno.objects.create(
            tutor=self.otro_tutor,
            alumno=self.alumno_ajeno,
        )

    def test_mis_hijos_requiere_autenticacion(
        self,
    ):

        response = self.client.get(reverse("api:mis_hijos"))

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_tutor_ve_solo_sus_hijos(
        self,
    ):

        self.client.force_authenticate(user=self.usuario_tutor)

        response = self.client.get(reverse("api:mis_hijos"))

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data["hijos"]),
            1,
        )

        self.assertEqual(
            response.data["hijos"][0]["id_alumno"],
            self.alumno.id_alumno,
        )

    def test_facturas_hijo(
        self,
    ):

        self.client.force_authenticate(user=self.usuario_tutor)

        response = self.client.get(
            reverse(
                "api:facturas_hijo",
                kwargs={
                    "id_alumno": self.alumno.id_alumno,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data["facturas"]),
            1,
        )

        factura = response.data["facturas"][0]

        self.assertEqual(
            factura["total"],
            "15000.00",
        )

        self.assertEqual(
            factura["saldo"],
            "15000.00",
        )

    def test_tutor_no_accede_a_alumno_ajeno(
        self,
    ):

        self.client.force_authenticate(user=self.usuario_tutor)

        response = self.client.get(
            reverse(
                "api:facturas_hijo",
                kwargs={
                    "id_alumno": self.alumno_ajeno.id_alumno,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_login_mobile_correcto(
        self,
    ):

        response = self.client.post(
            reverse("api:login_mobile"),
            {
                "username": "tutor_prueba",
                "password": "ClaveSegura123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "token",
            response.data,
        )

        self.assertEqual(
            response.data["usuario"]["rol"],
            PerfilUsuario.Rol.TUTOR,
        )

        self.assertTrue(Token.objects.filter(user=self.usuario_tutor).exists())

    def test_login_mobile_credenciales_incorrectas(
        self,
    ):

        response = self.client.post(
            reverse("api:login_mobile"),
            {
                "username": "tutor_prueba",
                "password": "password_incorrecto",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_token_permite_acceder_a_mis_hijos(
        self,
    ):

        login_response = self.client.post(
            reverse("api:login_mobile"),
            {
                "username": "tutor_prueba",
                "password": "ClaveSegura123!",
            },
            format="json",
        )

        token = login_response.data["token"]

        self.client.credentials(HTTP_AUTHORIZATION=(f"Token {token}"))

        response = self.client.get(reverse("api:mis_hijos"))

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data["hijos"]),
            1,
        )

        self.assertEqual(
            response.data["hijos"][0]["id_alumno"],
            self.alumno.id_alumno,
        )

    def test_logout_invalida_token(
        self,
    ):

        login_response = self.client.post(
            reverse("api:login_mobile"),
            {
                "username": "tutor_prueba",
                "password": "ClaveSegura123!",
            },
            format="json",
        )

        token = login_response.data["token"]

        self.client.credentials(HTTP_AUTHORIZATION=(f"Token {token}"))

        logout_response = self.client.post(reverse("api:logout_mobile"))

        self.assertEqual(
            logout_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertFalse(Token.objects.filter(user=self.usuario_tutor).exists())

        response = self.client.get(reverse("api:mis_hijos"))

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
