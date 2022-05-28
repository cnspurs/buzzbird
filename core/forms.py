from django import forms


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=16)
