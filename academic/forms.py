from django import forms
from .models import Alumno, Profesor, NivelEducativo, Materia, Horario, Curso, DictadoMateria, Tutor, TutorAlumno


class AlumnoForm(forms.ModelForm):

    class Meta:
        model = Alumno

        fields = [
            "dni",
            "legajo",
            "nombre",
            "apellido",
            "fecha_nacimiento",
            "domicilio",
            "telefono",
            "correo",
            "curso",
            "estado",
        ]

        widgets = {
            "dni": forms.TextInput(
                attrs={"placeholder": "Ingrese DNI"}
            ),
            "legajo": forms.TextInput(
                attrs={"placeholder": "Ingrese legajo"}
            ),
            "nombre": forms.TextInput(
                attrs={"placeholder": "Ingrese nombre"}
            ),
            "apellido": forms.TextInput(
                attrs={"placeholder": "Ingrese apellido"}
            ),
            "fecha_nacimiento": forms.DateInput(
                attrs={"type": "date"}
            ),
            "domicilio": forms.TextInput(
                attrs={"placeholder": "Ingrese domicilio"}
            ),
            "telefono": forms.TextInput(
                attrs={"placeholder": "Ingrese teléfono"}
            ),
            "correo": forms.EmailInput(
                attrs={"placeholder": "correo@ejemplo.com"}
            ),
        }

class AlumnoDatosPersonalesForm(forms.ModelForm):

    class Meta:
        model = Alumno

        fields = [
            "correo",
            "telefono",
            "domicilio",
        ]

        widgets = {
            "correo": forms.EmailInput(
                attrs={
                    "placeholder": "correo@ejemplo.com"
                }
            ),

            "telefono": forms.TextInput(
                attrs={
                    "placeholder": "Ingrese teléfono"
                }
            ),

            "domicilio": forms.TextInput(
                attrs={
                    "placeholder": "Ingrese domicilio"
                }
            ),
        }

class ProfesorForm(forms.ModelForm):

    class Meta:
        model = Profesor

        fields = [
            "dni",
            "legajo",
            "nombre",
            "apellido",
            "especialidad",
            "correo",
            "telefono",
            "estado",
        ]

        widgets = {
            "dni": forms.TextInput(
                attrs={"placeholder": "Ingrese DNI"}
            ),
            "legajo": forms.TextInput(
                attrs={"placeholder": "Ingrese legajo"}
            ),
            "nombre": forms.TextInput(
                attrs={"placeholder": "Ingrese nombre"}
            ),
            "apellido": forms.TextInput(
                attrs={"placeholder": "Ingrese apellido"}
            ),
            "especialidad": forms.TextInput(
                attrs={"placeholder": "Ingrese especialidad"}
            ),
            "correo": forms.EmailInput(
                attrs={"placeholder": "correo@ejemplo.com"}
            ),
            "telefono": forms.TextInput(
                attrs={"placeholder": "Ingrese teléfono"}
            ),
        }

class ProfesorDatosPersonalesForm(forms.ModelForm):

    class Meta:
        model = Profesor

        fields = [
            "correo",
            "telefono",
        ]

        widgets = {
            "correo": forms.EmailInput(
                attrs={
                    "placeholder": "correo@ejemplo.com"
                }
            ),

            "telefono": forms.TextInput(
                attrs={
                    "placeholder": "Ingrese teléfono"
                }
            ),
        }

class MateriaForm(forms.ModelForm):

    class Meta:
        model = Materia

        fields = [
            "nombre",
            "estado",
        ]

        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "placeholder": "Ingrese el nombre de la materia"
                }
            ),
        }

class HorarioForm(forms.ModelForm):

    class Meta:
        model = Horario

        fields = [
            "dia_semana",
            "hora_inicio",
            "hora_fin",
        ]

        widgets = {
            "hora_inicio": forms.TimeInput(
                attrs={"type": "time"}
            ),
            "hora_fin": forms.TimeInput(
                attrs={"type": "time"}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        hora_inicio = cleaned_data.get("hora_inicio")
        hora_fin = cleaned_data.get("hora_fin")

        if (
            hora_inicio
            and hora_fin
            and hora_fin <= hora_inicio
        ):
            self.add_error(
                "hora_fin",
                "La hora de finalización debe ser posterior a la hora de inicio."
            )

        return cleaned_data

class DictadoMateriaForm(forms.ModelForm):

    class Meta:
        model = DictadoMateria

        fields = [
            "materia",
            "profesor",
            "curso",
            "horario",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["materia"].queryset = (
            Materia.objects
            .filter(estado=True)
            .order_by("nombre")
        )

        self.fields["profesor"].queryset = (
            Profesor.objects
            .filter(estado=True)
            .order_by("apellido", "nombre")
        )

        self.fields["curso"].queryset = (
            Curso.objects
            .filter(estado=True)
            .select_related("nivel")
            .order_by(
                "nivel__nombre",
                "nombre",
                "division"
            )
        )

        self.fields["horario"].queryset = (
            Horario.objects
            .all()
            .order_by(
                "dia_semana",
                "hora_inicio"
            )
        )

    def clean(self):

        cleaned_data = super().clean()

        materia = cleaned_data.get("materia")
        profesor = cleaned_data.get("profesor")
        curso = cleaned_data.get("curso")
        horario = cleaned_data.get("horario")

        if materia and profesor and curso and horario:

            asignaciones = DictadoMateria.objects.filter(
                materia=materia,
                profesor=profesor,
                curso=curso,
                horario=horario
            )

            if self.instance.pk:
                asignaciones = asignaciones.exclude(
                    pk=self.instance.pk
                )

            if asignaciones.exists():
                raise forms.ValidationError(
                    "Esta asignación ya se encuentra registrada."
                )

        return cleaned_data

class NivelEducativoForm(forms.ModelForm):

    class Meta:
        model = NivelEducativo

        fields = [
            "nombre",
            "estado",
        ]

        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "placeholder": "Ej.: Inicial, Primario, Secundario"
                }
            ),
        }

class CursoForm(forms.ModelForm):

    class Meta:
        model = Curso

        fields = [
            "nombre",
            "division",
            "turno",
            "nivel",
            "estado",
        ]

        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "placeholder": "Ej.: 1°"
                }
            ),
            "division": forms.TextInput(
                attrs={
                    "placeholder": "Ej.: A"
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["nivel"].queryset = (
            NivelEducativo.objects
            .filter(estado=True)
            .order_by("nombre")
        )

    def clean(self):

        cleaned_data = super().clean()

        nombre = cleaned_data.get("nombre")
        division = cleaned_data.get("division")
        turno = cleaned_data.get("turno")
        nivel = cleaned_data.get("nivel")

        if nombre and division and turno and nivel:

            cursos = Curso.objects.filter(
                nombre__iexact=nombre,
                division__iexact=division,
                turno=turno,
                nivel=nivel
            )

            if self.instance.pk:
                cursos = cursos.exclude(
                    pk=self.instance.pk
                )

            if cursos.exists():
                raise forms.ValidationError(
                    "Ya existe un curso con el mismo nombre, división, turno y nivel."
                )

        return cleaned_data
    
class TutorForm(forms.ModelForm):

    class Meta:

        model = Tutor

        fields = [
            "dni",
            "nombre",
            "apellido",
            "domicilio",
            "telefono",
            "correo",
            "estado",
        ]

        widgets = {

            "dni": forms.TextInput(
                attrs={
                    "placeholder": "DNI"
                }
            ),

            "nombre": forms.TextInput(
                attrs={
                    "placeholder": "Nombre"
                }
            ),

            "apellido": forms.TextInput(
                attrs={
                    "placeholder": "Apellido"
                }
            ),

            "domicilio": forms.TextInput(
                attrs={
                    "placeholder": "Domicilio"
                }
            ),

            "telefono": forms.TextInput(
                attrs={
                    "placeholder": "Teléfono"
                }
            ),

            "correo": forms.EmailInput(
                attrs={
                    "placeholder": "Correo electrónico"
                }
            ),
        }

class TutorAlumnoForm(forms.ModelForm):

    class Meta:

        model = TutorAlumno

        fields = [
            "tutor",
            "alumno",
        ]

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["tutor"].queryset = (
            Tutor.objects
            .filter(estado=True)
            .order_by(
                "apellido",
                "nombre"
            )
        )

        self.fields["alumno"].queryset = (
            Alumno.objects
            .filter(estado=True)
            .select_related("curso")
            .order_by(
                "apellido",
                "nombre"
            )
        )

    def clean(self):

        cleaned_data = super().clean()

        tutor = cleaned_data.get("tutor")
        alumno = cleaned_data.get("alumno")

        if tutor and alumno:

            if TutorAlumno.objects.filter(
                tutor=tutor,
                alumno=alumno
            ).exists():

                raise forms.ValidationError(
                    "Este alumno ya se encuentra asociado "
                    "a este tutor."
                )

        return cleaned_data