from django import forms
from .models import RutaTransporte, ContratacionTransporte, ServicioComedor, ContratacionComedor
from academic.models import Alumno

class RutaTransporteForm(forms.ModelForm):

    class Meta:

        model = RutaTransporte

        fields = [
            "nombre",
            "descripcion",
            "valor_mensual",
            "estado",
        ]

        widgets = {

            "nombre": forms.TextInput(
                attrs={
                    "placeholder": "Ej.: Zona Centro"
                }
            ),

            "descripcion": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Descripción del recorrido"
                }
            ),

            "valor_mensual": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "min": "0"
                }
            ),
        }

    def clean_valor_mensual(self):

        valor = self.cleaned_data.get(
            "valor_mensual"
        )

        if valor is not None and valor <= 0:

            raise forms.ValidationError(
                "El valor mensual debe ser mayor a cero."
            )

        return valor

class ContratacionTransporteForm(forms.ModelForm):

    class Meta:

        model = ContratacionTransporte

        fields = [
            "alumno",
            "ruta",
            "mes",
            "anio",
            "estado",
        ]

        widgets = {
            "anio": forms.NumberInput(
                attrs={
                    "min": "2026",
                    "placeholder": "Ej.: 2027"
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["alumno"].queryset = (
            Alumno.objects
            .filter(estado=True)
            .order_by(
                "apellido",
                "nombre"
            )
        )

        self.fields["ruta"].queryset = (
            RutaTransporte.objects
            .filter(estado=True)
            .order_by("nombre")
        )

    def clean(self):

        cleaned_data = super().clean()

        alumno = cleaned_data.get("alumno")
        mes = cleaned_data.get("mes")
        anio = cleaned_data.get("anio")

        if alumno and mes and anio:

            contrataciones = (
                ContratacionTransporte.objects
                .filter(
                    alumno=alumno,
                    mes=mes,
                    anio=anio,
                )
            )

            if self.instance.pk:

                contrataciones = (
                    contrataciones.exclude(
                        pk=self.instance.pk
                    )
                )

            if contrataciones.exists():

                raise forms.ValidationError(
                    "El alumno ya posee una contratación "
                    "de transporte para ese mes y año."
                )

        return cleaned_data

class ServicioComedorForm(forms.ModelForm):

    class Meta:

        model = ServicioComedor

        fields = [
            "nombre",
            "descripcion",
            "valor_mensual",
            "estado",
        ]

        widgets = {

            "nombre": forms.TextInput(
                attrs={
                    "placeholder": "Ej.: Comedor Escolar"
                }
            ),

            "descripcion": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Descripción del servicio"
                }
            ),

            "valor_mensual": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "min": "0"
                }
            ),
        }

    def clean_valor_mensual(self):

        valor = self.cleaned_data.get(
            "valor_mensual"
        )

        if valor is not None and valor <= 0:

            raise forms.ValidationError(
                "El valor mensual debe ser mayor a cero."
            )

        return valor

class ContratacionComedorForm(forms.ModelForm):

    class Meta:

        model = ContratacionComedor

        fields = [
            "alumno",
            "servicio",
            "mes",
            "anio",
            "estado",
        ]

        widgets = {

            "anio": forms.NumberInput(
                attrs={
                    "min": "2026",
                    "placeholder": "Ej.: 2027"
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["alumno"].queryset = (
            Alumno.objects
            .filter(estado=True)
            .order_by(
                "apellido",
                "nombre"
            )
        )

        self.fields["servicio"].queryset = (
            ServicioComedor.objects
            .filter(estado=True)
            .order_by("nombre")
        )

    def clean(self):

        cleaned_data = super().clean()

        alumno = cleaned_data.get("alumno")
        mes = cleaned_data.get("mes")
        anio = cleaned_data.get("anio")

        if alumno and mes and anio:

            contrataciones = (
                ContratacionComedor.objects
                .filter(
                    alumno=alumno,
                    mes=mes,
                    anio=anio,
                )
            )

            if self.instance.pk:

                contrataciones = (
                    contrataciones.exclude(
                        pk=self.instance.pk
                    )
                )

            if contrataciones.exists():

                raise forms.ValidationError(
                    "El alumno ya posee una contratación "
                    "de comedor para ese mes y año."
                )

        return cleaned_data