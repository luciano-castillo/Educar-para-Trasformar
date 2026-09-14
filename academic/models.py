from django.db import models

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