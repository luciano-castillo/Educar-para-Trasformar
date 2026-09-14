from django import forms
from .models import Alumno


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