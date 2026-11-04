from django.core.validators import FileExtensionValidator
from django.db import models

from academic.models import NivelEducativo


class SolicitudInscripcion(models.Model):

    class Estado(models.TextChoices):

        PENDIENTE = (
            "PENDIENTE",
            "Pendiente"
        )

        APROBADA = (
            "APROBADA",
            "Aprobada"
        )

        RECHAZADA = (
            "RECHAZADA",
            "Rechazada"
        )


    id_solicitud = models.BigAutoField(
        primary_key=True
    )


    # ==========================================
    # DATOS DEL FUTURO ALUMNO
    # ==========================================

    nombre_alumno = models.CharField(
        max_length=100
    )

    apellido_alumno = models.CharField(
        max_length=100
    )

    dni_alumno = models.CharField(
        max_length=15
    )

    fecha_nacimiento = models.DateField()


    nivel_solicitado = models.ForeignKey(
        NivelEducativo,
        on_delete=models.PROTECT,
        related_name="solicitudes_inscripcion"
    )


    # ==========================================
    # ADULTO RESPONSABLE
    # ==========================================

    nombre_responsable = models.CharField(
        max_length=100
    )

    apellido_responsable = models.CharField(
        max_length=100
    )

    telefono = models.CharField(
        max_length=30
    )

    correo = models.EmailField(
        max_length=150
    )


    # ==========================================
    # SOLICITUD
    # ==========================================

    observaciones = models.TextField(
        blank=True
    )

    estado = models.CharField(
        max_length=10,
        choices=Estado.choices,
        default=Estado.PENDIENTE
    )

    fecha_solicitud = models.DateTimeField(
        auto_now_add=True
    )

    fecha_revision = models.DateTimeField(
        null=True,
        blank=True
    )


    class Meta:

        ordering = [
            "-fecha_solicitud"
        ]


    def __str__(self):

        return (
            f"{self.apellido_alumno}, "
            f"{self.nombre_alumno} - "
            f"{self.get_estado_display()}"
        )

class ConsultaContacto(models.Model):

    class Estado(models.TextChoices):

        PENDIENTE = (
            "PENDIENTE",
            "Pendiente"
        )

        RESPONDIDA = (
            "RESPONDIDA",
            "Respondida"
        )


    id_consulta = models.BigAutoField(
        primary_key=True
    )

    nombre = models.CharField(
        max_length=120
    )

    correo = models.EmailField(
        max_length=150
    )

    telefono = models.CharField(
        max_length=30,
        blank=True
    )

    asunto = models.CharField(
        max_length=150
    )

    mensaje = models.TextField()

    estado = models.CharField(
        max_length=10,
        choices=Estado.choices,
        default=Estado.PENDIENTE
    )

    fecha_consulta = models.DateTimeField(
        auto_now_add=True
    )

    fecha_respuesta = models.DateTimeField(
        null=True,
        blank=True
    )


    class Meta:

        ordering = [
            "-fecha_consulta"
        ]


    def __str__(self):

        return (
            f"{self.nombre} - "
            f"{self.asunto}"
        )

class Opinion(models.Model):

    class Estado(models.TextChoices):

        PENDIENTE = (
            "PENDIENTE",
            "Pendiente"
        )

        APROBADA = (
            "APROBADA",
            "Aprobada"
        )

        RECHAZADA = (
            "RECHAZADA",
            "Rechazada"
        )


    id_opinion = models.BigAutoField(
        primary_key=True
    )

    nombre = models.CharField(
        max_length=120
    )

    correo = models.EmailField(
        max_length=150,
        blank=True
    )

    comentario = models.TextField()

    estado = models.CharField(
        max_length=10,
        choices=Estado.choices,
        default=Estado.PENDIENTE
    )

    fecha_opinion = models.DateTimeField(
        auto_now_add=True
    )

    fecha_revision = models.DateTimeField(
        null=True,
        blank=True
    )


    class Meta:

        ordering = [
            "-fecha_opinion"
        ]


    def __str__(self):

        return (
            f"{self.nombre} - "
            f"{self.get_estado_display()}"
        )

class Noticia(models.Model):

    id_noticia = models.BigAutoField(
        primary_key=True
    )

    titulo = models.CharField(
        max_length=200
    )

    resumen = models.CharField(
        max_length=300
    )

    contenido = models.TextField()

    imagen = models.ImageField(
        upload_to="website/noticias/",
        null=True,
        blank=True
    )

    publicada = models.BooleanField(
        default=False
    )

    fecha_publicacion = models.DateTimeField(
        auto_now_add=True
    )

    fecha_modificacion = models.DateTimeField(
        auto_now=True
    )


    class Meta:

        ordering = [
            "-fecha_publicacion"
        ]


    def __str__(self):

        return self.titulo


class ImagenGaleria(models.Model):

    id_imagen = models.BigAutoField(
        primary_key=True
    )

    titulo = models.CharField(
        max_length=150
    )

    descripcion = models.TextField(
        blank=True
    )

    imagen = models.ImageField(
        upload_to="website/galeria/"
    )

    publicada = models.BooleanField(
        default=True
    )

    orden = models.PositiveIntegerField(
        default=0
    )

    fecha_carga = models.DateTimeField(
        auto_now_add=True
    )


    class Meta:

        ordering = [
            "orden",
            "-fecha_carga"
        ]


    def __str__(self):

        return self.titulo

class PostulacionEmpleo(models.Model):

    class Estado(models.TextChoices):

        PENDIENTE = (
            "PENDIENTE",
            "Pendiente"
        )

        REVISADA = (
            "REVISADA",
            "Revisada"
        )

        DESCARTADA = (
            "DESCARTADA",
            "Descartada"
        )


    class Area(models.TextChoices):

        DOCENCIA = (
            "DOCENCIA",
            "Docencia"
        )

        ADMINISTRACION = (
            "ADMINISTRACION",
            "Administración"
        )

        APOYO = (
            "APOYO",
            "Apoyo estudiantil"
        )

        DEPORTES = (
            "DEPORTES",
            "Deportes"
        )

        SERVICIOS = (
            "SERVICIOS",
            "Servicios"
        )

        OTRO = (
            "OTRO",
            "Otro"
        )


    id_postulacion = models.BigAutoField(
        primary_key=True
    )

    nombre = models.CharField(
        max_length=100
    )

    apellido = models.CharField(
        max_length=100
    )

    correo = models.EmailField(
        max_length=150
    )

    telefono = models.CharField(
        max_length=30
    )

    area_interes = models.CharField(
        max_length=20,
        choices=Area.choices
    )

    mensaje = models.TextField(
        blank=True
    )

    cv = models.FileField(
        upload_to="website/empleo/cv/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "pdf",
                    "doc",
                    "docx",
                ]
            )
        ]
    )

    estado = models.CharField(
        max_length=10,
        choices=Estado.choices,
        default=Estado.PENDIENTE
    )

    fecha_postulacion = models.DateTimeField(
        auto_now_add=True
    )

    fecha_revision = models.DateTimeField(
        null=True,
        blank=True
    )


    class Meta:

        ordering = [
            "-fecha_postulacion"
        ]


    def __str__(self):

        return (
            f"{self.apellido}, "
            f"{self.nombre} - "
            f"{self.get_area_interes_display()}"
        )
