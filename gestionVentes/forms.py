from django import forms
from .models import Ordonnance, CommandeVirtuelle

class CommandeVirtuelleForm(forms.ModelForm):
    image = forms.ImageField(label="Ajouter l'ordonnance", required=True)

    class Meta:
        model = CommandeVirtuelle
        fields = ['geolocalisation', 'consentement', 'mode_paiement']
        widgets = {
            'geolocalisation': forms.HiddenInput(),
            'mode_paiement': forms.RadioSelect()  # Custom styling may be required for image buttons
        }
        labels = {
            'geolocalisation': 'Géolocalisation',
            'consentement': 'J\'accepte les conditions de validation',
            'mode_paiement': 'Mode de paiement'
        }
        label_suffix = ''  # Enlever les deux-points après les labels

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Modifier les labels des champs pour enlever les deux-points
        self.fields['image'].label = "Ajouter l'ordonnance"
        self.fields['geolocalisation'].label = 'Géolocalisation'
        self.fields['consentement'].label = 'J\'accepte les conditions de validation'
        self.fields['mode_paiement'].label = 'Mode de paiement'

        # Définir les choix pour le champ 'mode_paiement'
        self.fields['mode_paiement'].choices = [
            ('tmoney', 'Tmoney'),
            ('flooz', 'Flooz')
        ]

    def save(self, commit=True):
        formulaire_commande = super().save(commit=False)
        ordonnance = Ordonnance(image=self.cleaned_data['image'])
        if commit:
            ordonnance.save()
            formulaire_commande.ordonnance = ordonnance
            formulaire_commande.save()
        return formulaire_commande

class DateRangeForm(forms.Form):
    start_date = forms.DateField(widget=forms.TextInput(attrs={
        'class': 'form-control search-date', 'placeholder': 'Start Date', 'data-provide': 'datepicker'
    }))
    end_date = forms.DateField(widget=forms.TextInput(attrs={
        'class': 'form-control search-date', 'placeholder': 'End Date', 'data-provide': 'datepicker'
    }))
