# forms.py
from django import forms
from .models import Ordonnance, Client

class OrdonnanceForm(forms.ModelForm):
    class Meta:
        model = Ordonnance
        fields = ['image']


