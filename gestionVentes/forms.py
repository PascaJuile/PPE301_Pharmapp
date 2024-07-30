from django import forms
from .models import Ordonnance, FormulaireCommande

class FormulaireCommandeForm(forms.ModelForm):
    image = forms.ImageField(label="Ajouter l'ordonnance", required=True)

    class Meta:
        model = FormulaireCommande
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
