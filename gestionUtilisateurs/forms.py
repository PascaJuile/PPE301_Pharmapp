# gestionUtilisateurs/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Client, GestionnairePharmacie, PreparateurEnPharmacie, Caissier, Pharmacien, Livreur

ROLE_CHOICES = [
    ('GestionnairePharmacie', 'Gestionnaire de Pharmacie'),
    ('PreparateurEnPharmacie', 'Préparateur en Pharmacie'),
    ('Caissier', 'Caissier'),
    ('Client', 'Client'),
    ('Pharmacien', 'Pharmacien'),
    ('Livreur', 'Livreur'),
]

class InscriptionForm(forms.ModelForm):
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)

    class Meta:
        model = Client
        fields = ['nomUtilisateur', 'prenomUtilisateur', 'numeroUtilisateur', 'adresseUtilisateur', 'emailUtilisateur', 'motDePasse', 'role']
        widgets = {
            'motDePasse': forms.PasswordInput(),
        }

class ConnexionForm(forms.Form):
    email = forms.EmailField(label="Adresse Email", required=True)
    motDePasse = forms.CharField(label="Mot de Passe", widget=forms.PasswordInput, required=True)

class EditProfileForm(forms.ModelForm):
    mobile = forms.CharField(max_length=15, required=True)
    address = forms.CharField(max_length=255, required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']