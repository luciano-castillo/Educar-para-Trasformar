from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class NivelEducativo(models.Model):
    id_nivel = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=50, unique=True)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Curso(models.Model):

    TURNOS = [
        ("MANANA", "Mañana"),
        ("TARDE", "Tarde"),
        ("NOCHE", "Noche"),
    ]

    id_curso = models.BigAutoField(primary_key=True)

    nombre = models.CharField(
        max_length=50
    )

    division = models.CharField(
        max_length=10
    )

    turno = models.CharField(
        max_length=10,
        choices=TURNOS
    )

    nivel = models.ForeignKey(
        NivelEducativo,
        on_delete=models.PROTECT,
        related_name="cursos"
    )

    estado = models.BooleanField(
        default=True
    )

    def __str__(self):
        return f"{self.nombre} {self.division} - {self.nivel.nombre}"
    
class Alumno(models.Model):
    id_alumno = models.BigAutoField(primary_key=True)
    
    usuario = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="alumno"
    )

    dni = models.CharField(
        max_length=15,
        unique=True
    )

    legajo = models.CharField(
        max_length=20,
        unique=True
    )

    nombre = models.CharField(
        max_length=100
    )

    apellido = models.CharField(
        max_length=100
    )

    fecha_nacimiento = models.DateField()

    domicilio = models.CharField(
        max_length=150
    )

    telefono = models.CharField(
        max_length=30
    )

    correo = models.EmailField(
        max_length=150
    )

    curso = models.ForeignKey(
        Curso,
        on_delete=models.PROTECT,
        related_name="alumnos"
    )

    estado = models.BooleanField(
        default=True
    )

    def __str__(self):
        return f"{self.apellido}, {self.nombre} - Legajo {self.legajo}"

class Profesor(models.Model):
    id_profesor = models.BigAutoField(primary_key=True)

    usuario = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="profesor"
    )

    dni = models.CharField(
        max_length=15,
        unique=True
    )

    legajo = models.CharField(
        max_length=20,
        unique=True
    )

    nombre = models.CharField(
        max_length=100
    )

    apellido = models.CharField(
        max_length=100
    )

    especialidad = models.CharField(
        max_length=100
    )

    correo = models.EmailField(
        max_length=150
    )

    telefono = models.CharField(
        max_length=30
    )

    estado = models.BooleanField(
        default=True
    )

    def __str__(self):
        return f"{self.apellido}, {self.nombre} - Legajo {self.legajo}"

class Tutor(models.Model):

    id_tutor = models.BigAutoField(
        primary_key=True
    )

    usuario = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tutor"
    )

    dni = models.CharField(
        max_length=15,
        unique=True
    )

    nombre = models.CharField(
        max_length=100
    )

    apellido = models.CharField(
        max_length=100
    )

    domicilio = models.CharField(
        max_length=150
    )

    telefono = models.CharField(
        max_length=30
    )

    correo = models.EmailField(
        max_length=150
    )

    estado = models.BooleanField(
        default=True
    )

    def __str__(self):
        return (
            f"{self.apellido}, "
            f"{self.nombre} - DNI {self.dni}"
        )

class TutorAlumno(models.Model):

    id_relacion = models.BigAutoField(
        primary_key=True
    )

    tutor = models.ForeignKey(
        Tutor,
        on_delete=models.PROTECT,
        related_name="alumnos_asociados"
    )

    alumno = models.ForeignKey(
        Alumno,
        on_delete=models.PROTECT,
        related_name="tutores_asociados"
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "tutor",
                    "alumno",
                ],
                name="tutor_alumno_unico"
            )
        ]

    def __str__(self):

        return (
            f"{self.tutor.apellido}, "
            f"{self.tutor.nombre} → "
            f"{self.alumno.apellido}, "
            f"{self.alumno.nombre}"
        )

class Materia(models.Model):
    id_materia = models.BigAutoField(primary_key=True)

    nombre = models.CharField(
        max_length=100,
        unique=True
    )

    estado = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.nombre

class Horario(models.Model):

    DIAS = [
        ("LUNES", "Lunes"),
        ("MARTES", "Martes"),
        ("MIERCOLES", "Miércoles"),
        ("JUEVES", "Jueves"),
        ("VIERNES", "Viernes"),
        ("SABADO", "Sábado"),
    ]

    id_horario = models.BigAutoField(primary_key=True)

    dia_semana = models.CharField(
        max_length=10,
        choices=DIAS
    )

    hora_inicio = models.TimeField()

    hora_fin = models.TimeField()

    def __str__(self):
        return (
            f"{self.get_dia_semana_display()} "
            f"{self.hora_inicio.strftime('%H:%M')} - "
            f"{self.hora_fin.strftime('%H:%M')}"
        )

class DictadoMateria(models.Model):
    id_dictado = models.BigAutoField(primary_key=True)

    materia = models.ForeignKey(
        Materia,
        on_delete=models.PROTECT,
        related_name="dictados"
    )

    profesor = models.ForeignKey(
        Profesor,
        on_delete=models.PROTECT,
        related_name="dictados"
    )

    curso = models.ForeignKey(
        Curso,
        on_delete=models.PROTECT,
        related_name="dictados"
    )

    horario = models.ForeignKey(
        Horario,
        on_delete=models.PROTECT,
        related_name="dictados"
    )

    def __str__(self):
        return (
            f"{self.materia.nombre} - "
            f"{self.curso.nombre} {self.curso.division} - "
            f"{self.profesor.apellido}"
        )

class Asistencia(models.Model):

    ESTADOS = [
        ("PRESENTE", "Presente"),
        ("AUSENTE", "Ausente"),
        ("TARDE", "Tarde"),
        ("JUSTIFICADO", "Justificado"),
    ]

    id_asistencia = models.BigAutoField(
        primary_key=True
    )

    alumno = models.ForeignKey(
        Alumno,
        on_delete=models.PROTECT,
        related_name="asistencias"
    )

    dictado = models.ForeignKey(
        DictadoMateria,
        on_delete=models.PROTECT,
        related_name="asistencias"
    )

    fecha = models.DateField()

    estado = models.CharField(
        max_length=12,
        choices=ESTADOS,
        default="PRESENTE"
    )

    observaciones = models.CharField(
        max_length=250,
        blank=True
    )

    fecha_registro = models.DateTimeField(
        auto_now_add=True
    )

    fecha_modificacion = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "alumno",
                    "dictado",
                    "fecha",
                ],
                name="asistencia_alumno_dictado_fecha_unica"
            )
        ]

        ordering = [
            "-fecha",
            "alumno__apellido",
            "alumno__nombre",
        ]

    def clean(self):

        super().clean()

        if (
            self.alumno_id
            and
            self.dictado_id
            and
            self.alumno.curso_id
            != self.dictado.curso_id
        ):

            raise ValidationError(
                {
                    "alumno": (
                        "El alumno no pertenece "
                        "al curso de este dictado."
                    )
                }
            )

    def __str__(self):

        return (
            f"{self.alumno.apellido}, "
            f"{self.alumno.nombre} - "
            f"{self.dictado.materia.nombre} - "
            f"{self.fecha} - "
            f"{self.get_estado_display()}"
        )

class Nota(models.Model):

    id_nota = models.BigAutoField(
        primary_key=True
    )

    alumno = models.ForeignKey(
        Alumno,
        on_delete=models.PROTECT,
        related_name="notas"
    )

    dictado = models.ForeignKey(
        DictadoMateria,
        on_delete=models.PROTECT,
        related_name="notas"
    )

    periodo = models.CharField(
        max_length=50
    )

    evaluacion = models.CharField(
        max_length=100
    )

    calificacion = models.DecimalField(
        max_digits=4,
        decimal_places=2
    )

    fecha = models.DateField()

    observaciones = models.CharField(
        max_length=250,
        blank=True
    )

    fecha_registro = models.DateTimeField(
        auto_now_add=True
    )

    fecha_modificacion = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "alumno",
                    "dictado",
                    "periodo",
                    "evaluacion",
                ],
                name="nota_alumno_dictado_periodo_evaluacion_unica"
            ),

            models.CheckConstraint(
                condition=(
                    models.Q(
                        calificacion__gte=1
                    )
                    &
                    models.Q(
                        calificacion__lte=10
                    )
                ),
                name="nota_calificacion_entre_1_y_10"
            ),
        ]

        ordering = [
            "-fecha",
            "alumno__apellido",
            "alumno__nombre",
        ]

    def clean(self):

        super().clean()

        if (
            self.alumno_id
            and
            self.dictado_id
            and
            self.alumno.curso_id
            != self.dictado.curso_id
        ):

            raise ValidationError(
                {
                    "alumno": (
                        "El alumno no pertenece "
                        "al curso de este dictado."
                    )
                }
            )

        if (
            self.calificacion is not None
            and
            (
                self.calificacion < 1
                or
                self.calificacion > 10
            )
        ):

            raise ValidationError(
                {
                    "calificacion": (
                        "La calificación debe estar "
                        "entre 1 y 10."
                    )
                }
            )

    def __str__(self):

        return (
            f"{self.alumno.apellido}, "
            f"{self.alumno.nombre} - "
            f"{self.dictado.materia.nombre} - "
            f"{self.evaluacion} - "
            f"{self.calificacion}"
        )