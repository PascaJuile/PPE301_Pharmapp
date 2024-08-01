from decimal import Decimal
import uuid
from django.db import models
from gestionStocks.models import Medicament
from gestionUtilisateurs.models import Caissier,Client,Pharmacien,Livreur

class Ordonnance(models.Model):
    image = models.ImageField(upload_to='ordonnance_images/', verbose_name='Photo', blank=False)
    ordonnance_client = models.ForeignKey(Client, on_delete=models.CASCADE)

class CommandeVirtuelle(models.Model):
    ordonnance = models.OneToOneField(Ordonnance, on_delete=models.CASCADE)
    geolocalisation = models.CharField(max_length=255, blank=True, null=True)
    date_commande = models.DateTimeField(auto_now_add=True)
    consentement = models.BooleanField(default=False)
    mode_paiement = models.CharField(max_length=50, choices=[('tmoney', 'Tmoney'), ('flooz', 'Flooz')])
    etat_validation = models.BooleanField(default=False)
    motif = models.CharField(max_length=255, default="Ordonnance correcte" )

    def recuperer_mode_payement(self):
        choix = dict(self._meta.get_field('mode_paiement').choices)
        return choix.get(self.mode_paiement, 'Unknown')

class SelectionMedicament(models.Model):
    statut = models.CharField(max_length=50, choices=[('virtuelle', 'Virtuelle'), ('presentiel', 'Presentiel')])
    donnees = models.JSONField()
    dateCreation = models.DateTimeField(auto_now_add=True)
    etatDeValidation = models.BooleanField(default=False)
    pharmacien = models.ForeignKey(
        Pharmacien,
        on_delete=models.CASCADE
    )

    def recuperer_prix_total(self):
        total = 0
        # Retourner le prix total basé sur la méthode définie dans CommandePresentielle
        commande = CommandePresentielle.objects.filter(selection_medicaments=self).first()
        if commande:
            total = commande.prixTotal
        return total

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

class Livraison(models.Model):
    ordonnance = models.OneToOneField(Ordonnance, on_delete=models.CASCADE)
    livreur = models.ForeignKey(Livreur, on_delete=models.CASCADE)
    etat_de_livraison = models.BooleanField(default=False)

