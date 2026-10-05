from django import forms
from .models import Deporte, GrupoDeportivo, InscripcionDeporte
from academic.models import (
    NivelEducativo,
    Profesor,
    Horario,
    Alumno,
)


class DeporteForm(forms.ModelForm):

    class Meta:

        model = Deporte

        fields = [
            "nombre",
            "descripcion",
            "estado",
        ]

        widgets = {

            "nombre": forms.TextInput(
                attrs={
                    "placeholder": "Ej.: Fútbol"
                }
            ),

            "descripcion": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Descripción del deporte"
                }
            ),
        }

class GrupoDeportivoForm(forms.ModelForm):

    class Meta:
        model = GrupoDeportivo

        fields = [
            "deporte",
            "nivel",
            "profesor",
            "horario",
            "estado",
        ]

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["deporte"].queryset = (
            Deporte.objects
            .filter(estado=True)
            .order_by("nombre")
        )

        self.fields["nivel"].queryset = (
            NivelEducativo.objects
            .filter(estado=True)
            .order_by("nombre")
        )

        self.fields["profesor"].queryset = (
            Profesor.objects
            .filter(estado=True)
            .order_by("apellido", "nombre")
        )

        self.fields["horario"].queryset = (
            Horario.objects
            .all()
            .order_by("dia_semana", "hora_inicio")
        )

    def clean(self):

        cleaned_data = super().clean()

        deporte = cleaned_data.get("deporte")
        nivel = cleaned_data.get("nivel")
        profesor = cleaned_data.get("profesor")
        horario = cleaned_data.get("horario")

        if deporte and nivel and profesor and horario:

            grupos = GrupoDeportivo.objects.filter(
                deporte=deporte,
                nivel=nivel,
                profesor=profesor,
                horario=horario
            )

            if self.instance.pk:
                grupos = grupos.exclude(
                    pk=self.instance.pk
                )

            if grupos.exists():
                raise forms.ValidationError(
                    "Ya existe un grupo deportivo con el mismo "
                    "deporte, nivel, profesor y horario."
                )

        return cleaned_data

class InscripcionDeporteForm(forms.ModelForm):

    class Meta:

        model = InscripcionDeporte

        fields = [
            "alumno",
            "grupo",
        ]

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["alumno"].queryset = (
            Alumno.objects
            .filter(estado=True)
            .order_by("apellido", "nombre")
        )

        self.fields["grupo"].queryset = (
            GrupoDeportivo.objects
            .filter(
                estado=True,
                deporte__estado=True,
                nivel__estado=True,
            )
            .select_related(
                "deporte",
                "nivel",
                "profesor",
                "horario"
            )
            .order_by(
                "deporte__nombre",
                "nivel__nombre"
            )
        )

    def clean(self):

        cleaned_data = super().clean()

        alumno = cleaned_data.get("alumno")
        grupo = cleaned_data.get("grupo")

        if not alumno or not grupo:
            return cleaned_data

        inscripciones_activas = (
            InscripcionDeporte.objects
            .filter(
                alumno=alumno,
                estado=True
            )
            .select_related(
                "grupo",
                "grupo__deporte",
                "grupo__horario"
            )
        )

        # Si alguna vez reutilizamos este formulario
        # para editar una inscripción:
        if self.instance.pk:

            inscripciones_activas = (
                inscripciones_activas
                .exclude(pk=self.instance.pk)
            )

        # RF33:
        # No permitir dos inscripciones activas
        # en el mismo grupo.

        if inscripciones_activas.filter(
            grupo=grupo
        ).exists():

            raise forms.ValidationError(
                "El alumno ya se encuentra inscripto "
                "en este grupo deportivo."
            )

        # RF31:
        # Máximo dos deportes simultáneos.

        if inscripciones_activas.count() >= 2:

            raise forms.ValidationError(
                "El alumno ya participa en dos deportes. "
                "No puede realizar una tercera inscripción."
            )

        # RF32:
        # Verificar superposición horaria.

        nuevo_horario = grupo.horario

        for inscripcion in inscripciones_activas:

            horario_actual = (
                inscripcion.grupo.horario
            )

            mismo_dia = (
                horario_actual.dia_semana
                == nuevo_horario.dia_semana
            )

            hay_superposicion = (
                nuevo_horario.hora_inicio
                < horario_actual.hora_fin
                and
                nuevo_horario.hora_fin
                > horario_actual.hora_inicio
            )

            if mismo_dia and hay_superposicion:

                raise forms.ValidationError(
                    "El horario del grupo se superpone "
                    f"con {inscripcion.grupo.deporte.nombre} "
                    f"({horario_actual})."
                )

        return cleaned_data