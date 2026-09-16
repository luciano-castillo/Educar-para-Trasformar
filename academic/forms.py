from django import forms
from .models import Alumno, Profesor


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