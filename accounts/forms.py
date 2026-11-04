from django.contrib.auth.forms import SetPasswordForm


class CambioPasswordInicialForm(SetPasswordForm):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields[
            "new_password1"
        ].widget.attrs.update(
            {
                "placeholder": "Ingresá tu nueva contraseña",
                "autocomplete": "new-password",
            }
        )

        self.fields[
            "new_password2"
        ].widget.attrs.update(
            {
                "placeholder": "Repetí tu nueva contraseña",
                "autocomplete": "new-password",
            }
        )

        self.fields[
            "new_password1"
        ].label = "Nueva contraseña"

        self.fields[
            "new_password2"
        ].label = "Confirmar nueva contraseña"