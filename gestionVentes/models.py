from datetime import datetime
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
    etat_payement = models.BooleanField(default=False)
    etat_validation = models.BooleanField(default=False)
    motif = models.CharField(max_length=255, default="Ordonnance correcte" )

    def recuperer_mode_payement(self):
        choix = dict(self._meta.get_field('mode_paiement').choices)
        return choix.get(self.mode_paiement, 'Inconnu')
    
    def accepter_commande(self):
        self.etat_validation = True
        self.save()

class SelectionMedicament(models.Model):
    etatOrdonnance = models.BooleanField(default=False)
    statut = models.CharField(max_length=50, choices=[('virtuelle', 'Virtuelle'), ('presentiel', 'Presentiel')])
    donnees = models.JSONField()
    dateCreation = models.DateTimeField(auto_now_add=True)
    etatDeValidation = models.BooleanField(default=False)
    pharmacien = models.ForeignKey(
        Pharmacien,
        on_delete=models.CASCADE
    )
    ordonnance = models.ForeignKey(
        Ordonnance,
        on_delete=models.CASCADE,
        related_name='selections',
        null=True,
        blank=True  
    )
    reference_commande = models.CharField(max_length=100, unique=True, blank=True)

    def generate_reference_commande(self):
        try:
            # Préfixe de la pharmacie
            prefix = "PHAR"

            # Date actuelle au format YYYYMMDD
            date_str = datetime.now().strftime('%Y%m%d')
            print(f"Date String: {date_str}")  # Debug line

            # Générer un identifiant unique
            unique_id = SelectionMedicament.objects.count() + 1
            print(f"Unique ID: {unique_id}")  # Debug line

            # Construction du code unique
            reference_commande = f"{prefix}{date_str}{unique_id:05d}"
            print(f"Generated Reference Commande: {reference_commande}")  # Debug line

            return reference_commande
        except Exception as e:
            print(f"Error generating reference_commande: {e}")  # Error handling
            raise e

    def save(self, *args, **kwargs):
        if not self.reference_commande:
            print("Generating reference commande...")  # Debug line
            self.reference_commande = self.generate_reference_commande()
            print(f"Reference commande generated: {self.reference_commande}")  # Debug line
        else:
            print(f"Existing reference commande: {self.reference_commande}")  # Debug line

        super().save(*args, **kwargs)
    

    def recuperer_prix_total(self):
        total = 0
        # Retourner le prix total basé sur la méthode définie dans CommandePresentielle
        commande = CommandePresentielle.objects.filter(selection_medicaments=self).first()
        if commande:
            total = commande.prixTotal
        return total
    
    def livraison_assignee(self):
        return Livraison.objects.filter(ordonnance=self.ordonnance).exists()

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
    date_validation = models.DateTimeField(auto_now_add=True)
    ordonnance = models.OneToOneField(Ordonnance, on_delete=models.CASCADE)
    livreur = models.ForeignKey(Livreur, on_delete=models.CASCADE)
    etat_de_livraison = models.BooleanField(default=False)

