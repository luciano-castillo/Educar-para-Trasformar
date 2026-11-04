from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from academic.models import Alumno, NivelEducativo

from .models import SolicitudInscripcion


class SolicitudInscripcionSeleniumTest(
    StaticLiveServerTestCase
):

    @classmethod
    def setUpClass(cls):

        super().setUpClass()

        options = webdriver.ChromeOptions()

        options.add_argument(
            "--headless=new"
        )

        options.add_argument(
            "--window-size=1440,1200"
        )

        options.add_argument(
            "--no-sandbox"
        )

        options.add_argument(
            "--disable-dev-shm-usage"
        )

        cls.selenium = webdriver.Chrome(
            options=options
        )

        cls.selenium.implicitly_wait(5)


    @classmethod
    def tearDownClass(cls):

        cls.selenium.quit()

        super().tearDownClass()


    def setUp(self):

        self.nivel = (
            NivelEducativo.objects.create(
                nombre="Nivel Primario",
                estado=True
            )
        )


    def completar_formulario(
        self,
        dni,
        apellido,
        telefono,
        correo,
        observaciones=""
    ):

        self.selenium.get(
            
                f"{self.live_server_url}"
                "/inscripcion/"
            
        )

        datos = {
            "nombre_alumno": "Luciano",
            "apellido_alumno": apellido,
            "dni_alumno": dni,
            "nombre_responsable": "Carlos",
            "apellido_responsable": apellido,
            "telefono": telefono,
            "correo": correo,
            "observaciones": observaciones,
        }

        for campo, valor in datos.items():

            self.selenium.find_element(
                By.NAME,
                campo
            ).send_keys(
                valor
            )

        campo_fecha = (
            self.selenium.find_element(
                By.NAME,
                "fecha_nacimiento"
            )
        )

        self.selenium.execute_script(
            (
                "arguments[0].value = "
                "'2015-05-10';"
            ),
            campo_fecha
        )

        Select(
            self.selenium.find_element(
                By.NAME,
                "nivel_solicitado"
            )
        ).select_by_value(
            str(
                self.nivel.pk
            )
        )


    def enviar_formulario(self):

        boton_enviar = WebDriverWait(
            self.selenium,
            10
        ).until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "button[type='submit']"
                )
            )
        )

        self.selenium.execute_script(
            "arguments[0].click();",
            boton_enviar
        )


    def test_visitante_envia_solicitud_pendiente_sin_crear_alumno(
        self
    ):

        dni = "50123456"

        self.completar_formulario(
            dni=dni,
            apellido="Prueba",
            telefono="3624123456",
            correo="prueba@example.com",
            observaciones=(
                "Solicitud generada por Selenium."
            )
        )

        self.enviar_formulario()

        WebDriverWait(
            self.selenium,
            10
        ).until(
            EC.text_to_be_present_in_element(
                (
                    By.CLASS_NAME,
                    "web-mensajes"
                ),
                (
                    "Tu solicitud fue enviada "
                    "correctamente."
                )
            )
        )

        solicitud = (
            SolicitudInscripcion.objects.get(
                dni_alumno=dni
            )
        )

        self.assertEqual(
            solicitud.estado,
            SolicitudInscripcion
            .Estado
            .PENDIENTE
        )

        self.assertFalse(
            Alumno.objects.filter(
                dni=dni
            ).exists()
        )


    def test_no_permite_solicitud_pendiente_duplicada(
        self
    ):

        dni = "50123456"

        SolicitudInscripcion.objects.create(
            nombre_alumno="Luciano",
            apellido_alumno="Existente",
            dni_alumno=dni,
            fecha_nacimiento="2015-05-10",
            nivel_solicitado=self.nivel,
            nombre_responsable="Carlos",
            apellido_responsable="Existente",
            telefono="3624123456",
            correo="existente@example.com",
            estado=(
                SolicitudInscripcion
                .Estado
                .PENDIENTE
            ),
        )

        self.completar_formulario(
            dni=dni,
            apellido="Duplicado",
            telefono="3624987654",
            correo="duplicado@example.com"
        )

        self.enviar_formulario()

        WebDriverWait(
            self.selenium,
            10
        ).until(
            EC.text_to_be_present_in_element(
                (
                    By.CLASS_NAME,
                    "web-error"
                ),
                (
                    "Ya existe una solicitud "
                    "pendiente para este DNI."
                )
            )
        )

        self.assertEqual(
            SolicitudInscripcion.objects.filter(
                dni_alumno=dni,
                estado=(
                    SolicitudInscripcion
                    .Estado
                    .PENDIENTE
                )
            ).count(),
            1
        )

        self.assertFalse(
            Alumno.objects.filter(
                dni=dni
            ).exists()
        )