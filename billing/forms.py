from django import forms

from .models import CuotaMensual


class CuotaMensualForm(forms.ModelForm):

    class Meta:

        model = CuotaMensual

        fields = [
            "mes",
            "anio",
            "valor",
            "fecha_vencimiento",
            "estado",
        ]

        widgets = {

            "anio": forms.NumberInput(
                attrs={
                    "min": "2026",
                    "placeholder": "Ej.: 2027",
                }
            ),

            "valor": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "Ej.: 55000",
                }
            ),

            "fecha_vencimiento": forms.DateInput(
                attrs={
                    "type": "date"
                }
            ),
        }

    def clean_valor(self):

        valor = self.cleaned_data.get("valor")

        if valor is not None and valor <= 0:

            raise forms.ValidationError(
                "El valor de la cuota debe ser mayor a cero."
            )

        return valor

    def clean(self):

        cleaned_data = super().clean()

        mes = cleaned_data.get("mes")
        anio = cleaned_data.get("anio")

        if mes and anio:

            cuotas = CuotaMensual.objects.filter(
                mes=mes,
                anio=anio
            )

            if self.instance.pk:
                cuotas = cuotas.exclude(
                    pk=self.instance.pk
                )

            if cuotas.exists():

                raise forms.ValidationError(
                    "Ya existe una cuota registrada "
                    "para ese mes y año."
                )

        return cleaned_data