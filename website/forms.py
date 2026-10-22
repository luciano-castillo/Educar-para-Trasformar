from django import forms
from django.core.exceptions import ValidationError

from academic.models import (
    Alumno,
    NivelEducativo,
)

from .models import (
    SolicitudInscripcion,
    ConsultaContacto,
    Opinion,
    Noticia,
    ImagenGaleria,
    PostulacionEmpleo,
)


class SolicitudInscripcionForm(
    forms.ModelForm
):

    class Meta:

        model = SolicitudInscripcion

        fields = [
            "nombre_alumno",
            "apellido_alumno",
            "dni_alumno",
            "fecha_nacimiento",
            "nivel_solicitado",
            "nombre_responsable",
            "apellido_responsable",
            "telefono",
            "correo",
            "observaciones",
        ]

        widgets = {

            "nombre_alumno": (
                forms.TextInput(
                    attrs={
                        "placeholder": (
                            "Nombre del estudiante"
                        )
                    }
                )
            ),

            "apellido_alumno": (
                forms.TextInput(
                    attrs={
                        "placeholder": (
                            "Apellido del estudiante"
                        )
                    }
                )
            ),

            "dni_alumno": (
                forms.TextInput(
                    attrs={
                        "placeholder": "DNI"
                    }
                )
            ),

            "fecha_nacimiento": (
                forms.DateInput(
                    attrs={
                        "type": "date"
                    }
                )
            ),

            "nombre_responsable": (
                forms.TextInput(
                    attrs={
                        "placeholder": (
                            "Nombre del responsable"
                        )
                    }
                )
            ),

            "apellido_responsable": (
                forms.TextInput(
                    attrs={
                        "placeholder": (
                            "Apellido del responsable"
                        )
                    }
                )
            ),

            "telefono": (
                forms.TextInput(
                    attrs={
                        "placeholder": (
                            "Teléfono de contacto"
                        )
                    }
                )
            ),

            "correo": (
                forms.EmailInput(
                    attrs={
                        "placeholder": (
                            "correo@ejemplo.com"
                        )
                    }
                )
            ),

            "observaciones": (
                forms.Textarea(
                    attrs={
                        "rows": 4,
                        "placeholder": (
                            "Información adicional "
                            "(opcional)"
                        )
                    }
                )
            ),
        }


    def __init__(
        self,
        *args,
        **kwargs
    ):

        super().__init__(
            *args,
            **kwargs
        )

        self.fields[
            "nivel_solicitado"
        ].queryset = (
            NivelEducativo.objects
            .filter(
                estado=True
            )
            .order_by(
                "nombre"
            )
        )


        self.fields[
            "nombre_alumno"
        ].label = "Nombre"

        self.fields[
            "apellido_alumno"
        ].label = "Apellido"

        self.fields[
            "dni_alumno"
        ].label = "DNI"

        self.fields[
            "fecha_nacimiento"
        ].label = "Fecha de nacimiento"

        self.fields[
            "nivel_solicitado"
        ].label = "Nivel educativo"

        self.fields[
            "nombre_responsable"
        ].label = "Nombre"

        self.fields[
            "apellido_responsable"
        ].label = "Apellido"

        self.fields[
            "telefono"
        ].label = "Teléfono"

        self.fields[
            "correo"
        ].label = "Correo electrónico"

        self.fields[
            "observaciones"
        ].label = "Observaciones"


    def clean_dni_alumno(self):

        dni = (
            self.cleaned_data[
                "dni_alumno"
            ]
            .strip()
        )


        # Ya existe como alumno oficial.

        if Alumno.objects.filter(
            dni__iexact=dni
        ).exists():

            raise ValidationError(
                (
                    "Ya existe un alumno "
                    "registrado con este DNI."
                )
            )


        # Ya existe una solicitud pendiente.

        if SolicitudInscripcion.objects.filter(
            dni_alumno__iexact=dni,
            estado=(
                SolicitudInscripcion
                .Estado
                .PENDIENTE
            )
        ).exists():

            raise ValidationError(
                (
                    "Ya existe una solicitud "
                    "pendiente para este DNI."
                )
            )


        return dni
    
class ConsultaContactoForm(
    forms.ModelForm
):

    class Meta:

        model = ConsultaContacto

        fields = [
            "nombre",
            "correo",
            "telefono",
            "asunto",
            "mensaje",
        ]

        widgets = {

            "nombre": forms.TextInput(
                attrs={
                    "placeholder": (
                        "Nombre y apellido"
                    )
                }
            ),

            "correo": forms.EmailInput(
                attrs={
                    "placeholder": (
                        "correo@ejemplo.com"
                    )
                }
            ),

            "telefono": forms.TextInput(
                attrs={
                    "placeholder": (
                        "Teléfono (opcional)"
                    )
                }
            ),

            "asunto": forms.TextInput(
                attrs={
                    "placeholder": (
                        "Motivo de la consulta"
                    )
                }
            ),

            "mensaje": forms.Textarea(
                attrs={
                    "rows": 6,
                    "placeholder": (
                        "Escribí tu consulta..."
                    )
                }
            ),
        }


    def __init__(
        self,
        *args,
        **kwargs
    ):

        super().__init__(
            *args,
            **kwargs
        )

        self.fields[
            "nombre"
        ].label = "Nombre y apellido"

        self.fields[
            "correo"
        ].label = "Correo electrónico"

        self.fields[
            "telefono"
        ].label = "Teléfono"

        self.fields[
            "asunto"
        ].label = "Asunto"

        self.fields[
            "mensaje"
        ].label = "Mensaje"

class OpinionForm(
    forms.ModelForm
):

    class Meta:

        model = Opinion

        fields = [
            "nombre",
            "correo",
            "comentario",
        ]

        widgets = {

            "nombre": forms.TextInput(
                attrs={
                    "placeholder": (
                        "Nombre y apellido"
                    )
                }
            ),

            "correo": forms.EmailInput(
                attrs={
                    "placeholder": (
                        "Correo electrónico "
                        "(opcional)"
                    )
                }
            ),

            "comentario": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": (
                        "Contanos tu opinión..."
                    )
                }
            ),
        }


    def __init__(
        self,
        *args,
        **kwargs
    ):

        super().__init__(
            *args,
            **kwargs
        )

        self.fields[
            "nombre"
        ].label = "Nombre"

        self.fields[
            "correo"
        ].label = "Correo electrónico"

        self.fields[
            "comentario"
        ].label = "Tu opinión"

class NoticiaForm(
    forms.ModelForm
):

    class Meta:

        model = Noticia

        fields = [
            "titulo",
            "resumen",
            "contenido",
            "imagen",
            "publicada",
        ]

        widgets = {

            "titulo": forms.TextInput(
                attrs={
                    "placeholder": (
                        "Título de la noticia"
                    )
                }
            ),

            "resumen": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": (
                        "Breve resumen"
                    )
                }
            ),

            "contenido": forms.Textarea(
                attrs={
                    "rows": 8,
                    "placeholder": (
                        "Contenido completo "
                        "de la noticia"
                    )
                }
            ),
        }

class ImagenGaleriaForm(
    forms.ModelForm
):

    class Meta:

        model = ImagenGaleria

        fields = [
            "titulo",
            "descripcion",
            "imagen",
            "orden",
            "publicada",
        ]

        widgets = {

            "titulo": forms.TextInput(
                attrs={
                    "placeholder": (
                        "Título de la imagen"
                    )
                }
            ),

            "descripcion": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": (
                        "Descripción opcional"
                    )
                }
            ),

            "orden": forms.NumberInput(
                attrs={
                    "min": 0
                }
            ),
        }

class PostulacionEmpleoForm(
    forms.ModelForm
):

    class Meta:

        model = PostulacionEmpleo

        fields = [
            "nombre",
            "apellido",
            "correo",
            "telefono",
            "area_interes",
            "mensaje",
            "cv",
        ]

        widgets = {

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

            "correo": forms.EmailInput(
                attrs={
                    "placeholder": (
                        "correo@ejemplo.com"
                    )
                }
            ),

            "telefono": forms.TextInput(
                attrs={
                    "placeholder": (
                        "Teléfono de contacto"
                    )
                }
            ),

            "mensaje": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": (
                        "Contanos brevemente "
                        "sobre tu experiencia "
                        "o interés en formar "
                        "parte de la institución."
                    )
                }
            ),
        }


    def __init__(
        self,
        *args,
        **kwargs
    ):

        super().__init__(
            *args,
            **kwargs
        )

        self.fields[
            "area_interes"
        ].label = "Área de interés"

        self.fields[
            "mensaje"
        ].label = "Presentación"

        self.fields[
            "cv"
        ].label = "Currículum Vitae"


    def clean_cv(self):

        cv = self.cleaned_data[
            "cv"
        ]


        limite = (
            5 * 1024 * 1024
        )


        if cv.size > limite:

            raise forms.ValidationError(
                (
                    "El archivo no puede "
                    "superar los 5 MB."
                )
            )


        return cv
