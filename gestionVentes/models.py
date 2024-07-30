from decimal import Decimal
from django.db import models
from gestionStocks.models import Medicament
from gestionUtilisateurs.models import Caissier,Client,Pharmacien,Livreur

# Create your models here.
class Ordonnance(models.Model):
    image = models.ImageField(upload_to='ordonnance_images/', verbose_name='Photo', blank=False)
    ordonnance_client = models.ForeignKey(Client, on_delete=models.CASCADE)

class FormulaireCommande(models.Model):
    ordonnance = models.OneToOneField(Ordonnance, on_delete=models.CASCADE)
    geolocalisation = models.CharField(max_length=255, blank=True, null=True)
    date_commande = models.DateTimeField(auto_now_add=True)
    consentement = models.BooleanField(default=False)
    mode_paiement = models.CharField(max_length=50, choices=[('tmoney', 'Tmoney'), ('flooz', 'Flooz')])

class CommandeVirtuelle(models.Model):
    formulaire_commande = models.OneToOneField(FormulaireCommande, on_delete=models.CASCADE)
    pharmacien = models.ForeignKey(Pharmacien, on_delete=models.CASCADE)
    prix_total = models.IntegerField()
    etat_commande = models.BooleanField(default=False)

class PayementCommandeVirtuelle(models.Model):
    commande = models.OneToOneField(CommandeVirtuelle, on_delete=models.CASCADE)
    caissier = models.ForeignKey(Caissier, on_delete=models.CASCADE)
    date_validation = models.DateTimeField(auto_now_add=True)
    etat_de_livraison = models.BooleanField(default=False)

class Livraison(models.Model):
    ordonnance = models.OneToOneField(Ordonnance, on_delete=models.CASCADE)
    livreur = models.ForeignKey(Livreur, on_delete=models.CASCADE)
    etat_de_livraison = models.BooleanField(default=False)

class SelectionMedicament(models.Model):
    donnees = models.JSONField()
    dateCreation = models.DateTimeField(auto_now_add=True)
    etatDeValidation = models.BooleanField(default=False)
    pharmacien = models.ForeignKey(
        Pharmacien,
        on_delete=models.CASCADE
    )

class CommandePresentielle(models.Model):
    prixTotal= models.IntegerField()
    selection_medicaments = models.OneToOneField(SelectionMedicament, on_delete=models.CASCADE)
    caissier = models.ForeignKey(Caissier, on_delete=models.CASCADE)
    date_validation = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.selection_medicaments.etatDeValidation:
            self.selection_medicaments.etatDeValidation = True
            self.selection_medicaments.save()
        super().save(*args, **kwargs)