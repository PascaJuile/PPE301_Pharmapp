# gestionUtilisateurs/forms.py
from django import forms
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
