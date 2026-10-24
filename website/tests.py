import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import (
    SimpleUploadedFile,
)
from django.test import TestCase
from django.urls import reverse

from academic.models import NivelEducativo
from accounts.models import PerfilUsuario

from .models import (
    ConsultaContacto,
    ImagenGaleria,
    Noticia,
    Opinion,
    PostulacionEmpleo,
    SolicitudInscripcion,
)


class WebsitePublicoTestCase(TestCase):

    def test_home_publico_responde_correctamente(self):

        response = self.client.get(
            reverse("home")
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertContains(
            response,
            "Educar Para Transformar"
        )


    def test_home_contiene_acceso_al_campus(self):

        response = self.client.get(
            reverse("home")
        )

        self.assertContains(
            response,
            reverse("login")
        )
        
    def test_home_contiene_carrusel(self):

        response = self.client.get(
            reverse("home")
        )

        self.assertContains(
            response,
            "data-carrusel"
        )

        self.assertContains(
            response,
            "Nuestra institución"
        )

        self.assertContains(
            response,
            "Deportes"
        )

        self.assertContains(
            response,
            "Innovación"
        )
        
    def test_paginas_publicas_responden_correctamente(self):

        paginas = [
            "quienes_somos",
            "niveles",
            "bienestar",
            "galeria",
            "noticias",
            "contacto",
            "inscripcion",
            "empleo",
        ]

        for pagina in paginas:

            with self.subTest(
                pagina=pagina
            ):

                response = self.client.get(
                    reverse(pagina)
                )

                self.assertEqual(
                    response.status_code,
                    200
                )
                
    def test_home_contiene_navegacion_publica(self):

        response = self.client.get(
            reverse("home")
        )

        self.assertContains(
            response,
            reverse("quienes_somos")
        )

        self.assertContains(
            response,
            reverse("niveles")
        )

        self.assertContains(
            response,
            reverse("bienestar")
        )

        self.assertContains(
            response,
            reverse("inscripcion")
        )

        self.assertContains(
            response,
            reverse("login")
        )

class SolicitudInscripcionTestCase(
    TestCase
):

    def setUp(self):

        self.nivel = (
            NivelEducativo.objects.create(
                nombre="Primario",
                estado=True
            )
        )


        self.datos_validos = {

            "nombre_alumno": "Juan",

            "apellido_alumno": "Perez",

            "dni_alumno": "50123456",

            "fecha_nacimiento": (
                "2018-05-10"
            ),

            "nivel_solicitado": (
                self.nivel.id_nivel
            ),

            "nombre_responsable": "Maria",

            "apellido_responsable": "Perez",

            "telefono": "3624000000",

            "correo": (
                "maria@example.com"
            ),

            "observaciones": (
                "Solicitud de prueba"
            ),
        }


    def test_formulario_inscripcion_es_publico(
        self
    ):

        response = self.client.get(
            reverse("inscripcion")
        )

        self.assertEqual(
            response.status_code,
            200
        )


    def test_visitante_puede_enviar_solicitud(
        self
    ):

        response = self.client.post(
            reverse("inscripcion"),
            self.datos_validos
        )

        self.assertRedirects(
            response,
            reverse("inscripcion")
        )


        self.assertTrue(
            SolicitudInscripcion.objects
            .filter(
                dni_alumno="50123456",
                estado="PENDIENTE"
            )
            .exists()
        )


    def test_no_permite_dos_solicitudes_pendientes_mismo_dni(
        self
    ):

        self.client.post(
            reverse("inscripcion"),
            self.datos_validos
        )

        response = self.client.post(
            reverse("inscripcion"),
            self.datos_validos
        )


        self.assertEqual(
            response.status_code,
            200
        )


        self.assertEqual(
            SolicitudInscripcion.objects
            .filter(
                dni_alumno="50123456"
            )
            .count(),
            1
        )


    def test_lista_solicitudes_requiere_admin(
        self
    ):

        response = self.client.get(
            reverse(
                "solicitud_inscripcion_lista"
            )
        )

        self.assertRedirects(
            response,
            reverse("login")
        )


    def test_admin_puede_ver_solicitudes(
        self
    ):

        usuario = (
            User.objects.create_user(
                username="admin_web",
                password="Admin123!"
            )
        )

        PerfilUsuario.objects.create(
            usuario=usuario,
            rol=PerfilUsuario.Rol.ADMIN,
            debe_cambiar_password=False
        )


        SolicitudInscripcion.objects.create(

            nombre_alumno="Juan",

            apellido_alumno="Perez",

            dni_alumno="50123456",

            fecha_nacimiento="2018-05-10",

            nivel_solicitado=self.nivel,

            nombre_responsable="Maria",

            apellido_responsable="Perez",

            telefono="3624000000",

            correo="maria@example.com",

        )


        self.client.force_login(
            usuario
        )


        response = self.client.get(
            reverse(
                "solicitud_inscripcion_lista"
            )
        )


        self.assertEqual(
            response.status_code,
            200
        )


        self.assertContains(
            response,
            "Juan"
        )


    def test_admin_puede_aprobar_solicitud(
        self
    ):

        usuario = (
            User.objects.create_user(
                username="admin_aprobar",
                password="Admin123!"
            )
        )

        PerfilUsuario.objects.create(
            usuario=usuario,
            rol=PerfilUsuario.Rol.ADMIN,
            debe_cambiar_password=False
        )


        solicitud = (
            SolicitudInscripcion.objects
            .create(

                nombre_alumno="Juan",

                apellido_alumno="Perez",

                dni_alumno="50123456",

                fecha_nacimiento="2018-05-10",

                nivel_solicitado=self.nivel,

                nombre_responsable="Maria",

                apellido_responsable="Perez",

                telefono="3624000000",

                correo="maria@example.com",
            )
        )


        self.client.force_login(
            usuario
        )


        response = self.client.post(
            reverse(
                "solicitud_inscripcion_aprobar",
                args=[
                    solicitud.id_solicitud
                ]
            )
        )


        solicitud.refresh_from_db()


        self.assertEqual(
            solicitud.estado,
            (
                SolicitudInscripcion
                .Estado
                .APROBADA
            )
        )


        self.assertIsNotNone(
            solicitud.fecha_revision
        )


        self.assertEqual(
            response.status_code,
            302
        )

class ConsultaContactoTestCase(
    TestCase
):

    def setUp(self):

        self.datos_validos = {

            "nombre": "Maria Perez",

            "correo": "maria@example.com",

            "telefono": "3624000000",

            "asunto": "Consulta sobre inscripción",

            "mensaje": (
                "Quisiera recibir información."
            ),
        }


    def test_contacto_es_publico(
        self
    ):

        response = self.client.get(
            reverse("contacto")
        )

        self.assertEqual(
            response.status_code,
            200
        )


    def test_visitante_puede_enviar_consulta(
        self
    ):

        response = self.client.post(
            reverse("contacto"),
            self.datos_validos
        )

        self.assertRedirects(
            response,
            reverse("contacto")
        )


        self.assertTrue(
            ConsultaContacto.objects
            .filter(
                correo="maria@example.com",
                estado="PENDIENTE"
            )
            .exists()
        )


    def test_lista_consultas_requiere_admin(
        self
    ):

        response = self.client.get(
            reverse(
                "consulta_contacto_lista"
            )
        )

        self.assertRedirects(
            response,
            reverse("login")
        )


    def test_admin_puede_ver_consultas(
        self
    ):

        usuario = User.objects.create_user(
            username="admin_consultas",
            password="Admin123!"
        )

        PerfilUsuario.objects.create(
            usuario=usuario,
            rol=PerfilUsuario.Rol.ADMIN,
            debe_cambiar_password=False
        )


        ConsultaContacto.objects.create(
            **self.datos_validos
        )


        self.client.force_login(
            usuario
        )


        response = self.client.get(
            reverse(
                "consulta_contacto_lista"
            )
        )


        self.assertEqual(
            response.status_code,
            200
        )

        self.assertContains(
            response,
            "Consulta sobre inscripción"
        )


    def test_admin_puede_marcar_consulta_respondida(
        self
    ):

        usuario = User.objects.create_user(
            username="admin_respuesta",
            password="Admin123!"
        )

        PerfilUsuario.objects.create(
            usuario=usuario,
            rol=PerfilUsuario.Rol.ADMIN,
            debe_cambiar_password=False
        )


        consulta = (
            ConsultaContacto.objects.create(
                **self.datos_validos
            )
        )


        self.client.force_login(
            usuario
        )


        response = self.client.post(
            reverse(
                "consulta_contacto_responder",
                args=[
                    consulta.id_consulta
                ]
            )
        )


        consulta.refresh_from_db()


        self.assertEqual(
            consulta.estado,
            ConsultaContacto
            .Estado
            .RESPONDIDA
        )

        self.assertIsNotNone(
            consulta.fecha_respuesta
        )

        self.assertEqual(
            response.status_code,
            302
        )

class OpinionTestCase(
    TestCase
):

    def setUp(self):

        self.datos_validos = {

            "nombre": "Ana Gomez",

            "correo": "ana@example.com",

            "comentario": (
                "Me parece una excelente "
                "propuesta educativa."
            ),
        }


    def test_opiniones_es_publico(
        self
    ):

        response = self.client.get(
            reverse("opiniones")
        )

        self.assertEqual(
            response.status_code,
            200
        )


    def test_visitante_puede_enviar_opinion(
        self
    ):

        response = self.client.post(
            reverse("opiniones"),
            self.datos_validos
        )


        self.assertRedirects(
            response,
            reverse("opiniones")
        )


        self.assertTrue(
            Opinion.objects.filter(
                nombre="Ana Gomez",
                estado="PENDIENTE"
            ).exists()
        )


    def test_opinion_pendiente_no_es_publica(
        self
    ):

        Opinion.objects.create(
            **self.datos_validos
        )


        response = self.client.get(
            reverse("opiniones")
        )


        self.assertNotContains(
            response,
            (
                "Me parece una excelente "
                "propuesta educativa."
            )
        )


    def test_opinion_aprobada_es_publica(
        self
    ):

        Opinion.objects.create(
            **self.datos_validos,
            estado=(
                Opinion
                .Estado
                .APROBADA
            )
        )


        response = self.client.get(
            reverse("opiniones")
        )


        self.assertContains(
            response,
            (
                "Me parece una excelente "
                "propuesta educativa."
            )
        )


    def test_lista_opiniones_requiere_admin(
        self
    ):

        response = self.client.get(
            reverse("opinion_lista")
        )


        self.assertRedirects(
            response,
            reverse("login")
        )


    def test_admin_puede_aprobar_opinion(
        self
    ):

        usuario = User.objects.create_user(
            username="admin_opiniones",
            password="Admin123!"
        )


        PerfilUsuario.objects.create(
            usuario=usuario,
            rol=PerfilUsuario.Rol.ADMIN,
            debe_cambiar_password=False
        )


        opinion = Opinion.objects.create(
            **self.datos_validos
        )


        self.client.force_login(
            usuario
        )


        response = self.client.post(
            reverse(
                "opinion_aprobar",
                args=[
                    opinion.id_opinion
                ]
            )
        )


        opinion.refresh_from_db()


        self.assertEqual(
            opinion.estado,
            Opinion.Estado.APROBADA
        )


        self.assertIsNotNone(
            opinion.fecha_revision
        )


        self.assertEqual(
            response.status_code,
            302
        )

class ContenidoPublicoTestCase(
    TestCase
):

    def test_noticia_publicada_aparece(
        self
    ):

        Noticia.objects.create(
            titulo="Inicio del ciclo lectivo",
            resumen="Comienzan las actividades.",
            contenido="Contenido de prueba.",
            publicada=True
        )


        response = self.client.get(
            reverse("noticias")
        )


        self.assertContains(
            response,
            "Inicio del ciclo lectivo"
        )


    def test_noticia_oculta_no_aparece(
        self
    ):

        Noticia.objects.create(
            titulo="Noticia privada",
            resumen="No debe mostrarse.",
            contenido="Contenido.",
            publicada=False
        )


        response = self.client.get(
            reverse("noticias")
        )


        self.assertNotContains(
            response,
            "Noticia privada"
        )


    def test_detalle_noticia_oculta_devuelve_404(
        self
    ):

        noticia = Noticia.objects.create(
            titulo="Noticia oculta",
            resumen="Resumen.",
            contenido="Contenido.",
            publicada=False
        )


        response = self.client.get(
            reverse(
                "noticia_detalle",
                args=[
                    noticia.id_noticia
                ]
            )
        )


        self.assertEqual(
            response.status_code,
            404
        )


    def test_galeria_muestra_solo_imagenes_publicadas(
        self
    ):

        ImagenGaleria.objects.create(
            titulo="Imagen pública",
            imagen=(
                "website/galeria/"
                "publica.jpg"
            ),
            publicada=True
        )


        ImagenGaleria.objects.create(
            titulo="Imagen oculta",
            imagen=(
                "website/galeria/"
                "oculta.jpg"
            ),
            publicada=False
        )


        response = self.client.get(
            reverse("galeria")
        )


        self.assertContains(
            response,
            "Imagen pública"
        )


        self.assertNotContains(
            response,
            "Imagen oculta"
        )


    def test_gestion_noticias_requiere_admin(
        self
    ):

        response = self.client.get(
            reverse(
                "noticia_admin_lista"
            )
        )


        self.assertRedirects(
            response,
            reverse("login")
        )


    def test_gestion_galeria_requiere_admin(
        self
    ):

        response = self.client.get(
            reverse(
                "galeria_admin_lista"
            )
        )


        self.assertRedirects(
            response,
            reverse("login")
        )


    def test_admin_puede_cambiar_publicacion_noticia(
        self
    ):

        usuario = User.objects.create_user(
            username="admin_noticias",
            password="Admin123!"
        )


        PerfilUsuario.objects.create(
            usuario=usuario,
            rol=PerfilUsuario.Rol.ADMIN,
            debe_cambiar_password=False
        )


        noticia = Noticia.objects.create(
            titulo="Nueva noticia",
            resumen="Resumen.",
            contenido="Contenido.",
            publicada=False
        )


        self.client.force_login(
            usuario
        )


        self.client.post(
            reverse(
                "noticia_admin_publicacion",
                args=[
                    noticia.id_noticia
                ]
            )
        )


        noticia.refresh_from_db()


        self.assertTrue(
            noticia.publicada
        )
        
    def test_home_muestra_noticias_publicadas(
        self
    ):

        Noticia.objects.create(
            titulo="Noticia pública Home",
            resumen="Resumen de prueba.",
            contenido="Contenido.",
            publicada=True
        )


        Noticia.objects.create(
            titulo="Noticia oculta Home",
            resumen="No debe aparecer.",
            contenido="Contenido.",
            publicada=False
        )


        response = self.client.get(
            reverse("home")
        )


        self.assertContains(
            response,
            "Noticia pública Home"
        )


        self.assertNotContains(
            response,
            "Noticia oculta Home"
        )


    def test_home_muestra_solo_opiniones_aprobadas(
        self
    ):

        Opinion.objects.create(
            nombre="Opinion Publica",
            comentario="Comentario aprobado Home",
            estado=Opinion.Estado.APROBADA
        )


        Opinion.objects.create(
            nombre="Opinion Pendiente",
            comentario="Comentario pendiente Home",
            estado=Opinion.Estado.PENDIENTE
        )


        response = self.client.get(
            reverse("home")
        )


        self.assertContains(
            response,
            "Comentario aprobado Home"
        )


        self.assertNotContains(
            response,
            "Comentario pendiente Home"
        )


    def test_home_usa_galeria_publicada_en_carrusel(
        self
    ):

        ImagenGaleria.objects.create(
            titulo="Fachada institucional",
            descripcion="Imagen del edificio",
            imagen=(
                "website/galeria/"
                "fachada.jpg"
            ),
            publicada=True,
            orden=0
        )


        ImagenGaleria.objects.create(
            titulo="Imagen oculta Home",
            imagen=(
                "website/galeria/"
                "oculta-home.jpg"
            ),
            publicada=False,
            orden=1
        )


        response = self.client.get(
            reverse("home")
        )


        self.assertContains(
            response,
            "Fachada institucional"
        )


        self.assertNotContains(
            response,
            "Imagen oculta Home"
        )

class PostulacionEmpleoTestCase(
    TestCase
):

    def setUp(self):

        self.media_temporal = (
            tempfile.TemporaryDirectory()
        )

        self.config_media = self.settings(
            MEDIA_ROOT=(
                self.media_temporal.name
            )
        )

        self.config_media.enable()

        self.addCleanup(
            self.config_media.disable
        )

        self.addCleanup(
            self.media_temporal.cleanup
        )


    def crear_cv(
        self,
        nombre="curriculum.pdf"
    ):

        return SimpleUploadedFile(
            nombre,
            b"Contenido CV de prueba",
            content_type="application/pdf"
        )


    def test_empleo_es_publico(
        self
    ):

        response = self.client.get(
            reverse("empleo")
        )

        self.assertEqual(
            response.status_code,
            200
        )


    def test_visitante_puede_enviar_postulacion(
        self
    ):

        response = self.client.post(
            reverse("empleo"),
            {
                "nombre": "Laura",
                "apellido": "Gomez",
                "correo": "laura@example.com",
                "telefono": "3624000000",
                "area_interes": "DOCENCIA",
                "mensaje": (
                    "Me interesa formar "
                    "parte del equipo."
                ),
                "cv": self.crear_cv(),
            }
        )


        self.assertRedirects(
            response,
            reverse("empleo")
        )


        self.assertTrue(
            PostulacionEmpleo.objects
            .filter(
                correo="laura@example.com",
                estado="PENDIENTE"
            )
            .exists()
        )


    def test_no_acepta_extension_cv_invalida(
        self
    ):

        archivo = SimpleUploadedFile(
            "archivo.exe",
            b"archivo",
            content_type=(
                "application/"
                "octet-stream"
            )
        )


        response = self.client.post(
            reverse("empleo"),
            {
                "nombre": "Laura",
                "apellido": "Gomez",
                "correo": "laura@example.com",
                "telefono": "3624000000",
                "area_interes": "DOCENCIA",
                "mensaje": "",
                "cv": archivo,
            }
        )


        self.assertEqual(
            response.status_code,
            200
        )


        self.assertFalse(
            PostulacionEmpleo.objects
            .filter(
                correo="laura@example.com"
            )
            .exists()
        )


    def test_gestion_empleo_requiere_admin(
        self
    ):

        response = self.client.get(
            reverse(
                "empleo_admin_lista"
            )
        )


        self.assertRedirects(
            response,
            reverse("login")
        )


    def test_admin_puede_ver_postulaciones(
        self
    ):

        usuario = User.objects.create_user(
            username="admin_empleo",
            password="Admin123!"
        )


        PerfilUsuario.objects.create(
            usuario=usuario,
            rol=PerfilUsuario.Rol.ADMIN,
            debe_cambiar_password=False
        )


        PostulacionEmpleo.objects.create(
            nombre="Laura",
            apellido="Gomez",
            correo="laura@example.com",
            telefono="3624000000",
            area_interes="DOCENCIA",
            cv=self.crear_cv()
        )


        self.client.force_login(
            usuario
        )


        response = self.client.get(
            reverse(
                "empleo_admin_lista"
            )
        )


        self.assertEqual(
            response.status_code,
            200
        )


        self.assertContains(
            response,
            "Laura"
        )


    def test_admin_puede_marcar_postulacion_revisada(
        self
    ):

        usuario = User.objects.create_user(
            username="admin_rrhh",
            password="Admin123!"
        )


        PerfilUsuario.objects.create(
            usuario=usuario,
            rol=PerfilUsuario.Rol.ADMIN,
            debe_cambiar_password=False
        )


        postulacion = (
            PostulacionEmpleo.objects.create(
                nombre="Laura",
                apellido="Gomez",
                correo="laura@example.com",
                telefono="3624000000",
                area_interes="DOCENCIA",
                cv=self.crear_cv()
            )
        )


        self.client.force_login(
            usuario
        )


        response = self.client.post(
            reverse(
                "empleo_admin_revisar",
                args=[
                    postulacion.id_postulacion
                ]
            )
        )


        postulacion.refresh_from_db()


        self.assertEqual(
            postulacion.estado,
            (
                PostulacionEmpleo
                .Estado
                .REVISADA
            )
        )


        self.assertIsNotNone(
            postulacion.fecha_revision
        )


        self.assertEqual(
            response.status_code,
            302
        )
