from django.db import models
from django.contrib.auth.models import User

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