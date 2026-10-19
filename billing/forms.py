from django import forms
from decimal import Decimal

from .models import CuotaMensual, DetalleFactura
from academic.models import Alumno

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


class GenerarFacturaForm(forms.Form):

    alumno = forms.ModelChoiceField(
        queryset=Alumno.objects.none(),
        label="Alumno"
    )

    mes = forms.ChoiceField(
        choices=CuotaMensual.MESES,
        label="Mes"
    )

    anio = forms.IntegerField(
        label="Año",
        min_value=2026,
        widget=forms.NumberInput(
            attrs={
                "placeholder": "Ej.: 2026"
            }
        )
    )

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

class RegistrarPagoForm(forms.Form):

    fecha_transferencia = forms.DateField(
        label="Fecha de transferencia",
        widget=forms.DateInput(
            attrs={
                "type": "date"
            }
        )
    )

    numero_operacion = forms.CharField(
        label="Número de operación",
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Ej.: 123456789"
            }
        )
    )

    observaciones = forms.CharField(
        label="Observaciones",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "Observaciones del pago"
            }
        )
    )

    def __init__(
        self,
        *args,
        factura=None,
        **kwargs
    ):

        super().__init__(
            *args,
            **kwargs
        )

        self.factura = factura

        if not factura:
            return

        detalles = (
            factura.detalles
            .all()
            .order_by(
                "id_detalle"
            )
        )

        for detalle in detalles:

            disponible = (
                detalle.saldo_disponible_pago
            )

            if disponible <= 0:
                continue

            nombre_campo = (
                f"concepto_{detalle.id_detalle}"
            )

            self.fields[
                nombre_campo
            ] = forms.DecimalField(
                label=(
                    f"{detalle.descripcion} "
                    f"- Disponible: ${disponible}"
                ),
                required=False,
                min_value=Decimal("0.01"),
                max_value=disponible,
                decimal_places=2,
                max_digits=10,
                widget=forms.NumberInput(
                    attrs={
                        "step": "0.01",
                        "placeholder": "0.00"
                    }
                )
            )

    def clean(self):

        cleaned_data = super().clean()

        if not self.factura:
            return cleaned_data

        aplicaciones = []

        for nombre, importe in (
            cleaned_data.items()
        ):

            if not nombre.startswith(
                "concepto_"
            ):
                continue

            if importe in (
                None,
                "",
            ):
                continue

            id_detalle = int(
                nombre.replace(
                    "concepto_",
                    ""
                )
            )

            try:

                detalle = (
                    self.factura.detalles
                    .get(
                        id_detalle=id_detalle
                    )
                )

            except DetalleFactura.DoesNotExist:

                raise forms.ValidationError(
                    "Uno de los conceptos "
                    "seleccionados no pertenece "
                    "a esta factura."
                )

            disponible = (
                detalle.saldo_disponible_pago
            )

            if importe > disponible:

                raise forms.ValidationError(
                    f"El importe de "
                    f"'{detalle.descripcion}' "
                    f"supera el saldo disponible."
                )

            aplicaciones.append(
                (
                    detalle,
                    importe,
                )
            )

        if not aplicaciones:

            raise forms.ValidationError(
                "Debe ingresar un importe "
                "en al menos un concepto."
            )

        cleaned_data[
            "aplicaciones"
        ] = aplicaciones

        return cleaned_data