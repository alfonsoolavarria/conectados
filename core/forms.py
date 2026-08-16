from django import forms
from django.contrib.auth import authenticate


class LoginForm(forms.Form):
    identifier = forms.CharField(
        label="Camp Code or Email",
        max_length=254,
        widget=forms.TextInput(
            attrs={
                "id": "identifier",
                "placeholder": "e.g. HVYC-2024",
                "autocomplete": "username",
            }
        ),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "id": "password",
                "placeholder": "••••••••",
                "autocomplete": "current-password",
            }
        ),
    )

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean(self):
        cleaned_data = super().clean()
        identifier = cleaned_data.get("identifier")
        password = cleaned_data.get("password")

        if identifier and password:
            user = authenticate(
                self.request, username=identifier, password=password
            )
            if user is None:
                raise forms.ValidationError(
                    "Camp code o contraseña incorrectos. Intenta de nuevo."
                )
            self.user_cache = user
        return cleaned_data

    def get_user(self):
        return getattr(self, "user_cache", None)
