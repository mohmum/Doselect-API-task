from django.contrib.auth.models import User
from django import forms

class Loginform(forms.Form):
    class Meta:
        model =User
        fields = ['username','password']
