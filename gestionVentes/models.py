from decimal import Decimal
from django.db import models
from gestionStocks.models import Medicament
from gestionUtilisateurs.models import Caissier,Client,Pharmacien,Livreur

# Create your models here.
class Ordonnance(models.Model):
    image = models.ImageField(upload_to='ordonnance_images/', verbose_name='Photo', blank=False)
    ordonnanceClient = models.ForeignKey(
        Client,
        on_delete= models.CASCADE
    )
    ordonnancePharmacien=models.ForeignKey(
        Pharmacien,
        on_delete= models.CASCADE
    )


class CommandeVirtuelle(models.Model):
    prixTotal= models.IntegerField()
    dateCommande = models.DateTimeField()
    etatDeCommande = models.BooleanField(default=False)
    etatDeLivraison = models.BooleanField(default=False)

    commandeOrdonnance = models.OneToOneField(
        Ordonnance,
        on_delete= models.CASCADE
    )
    commandeCaissier = models.ForeignKey(
        Caissier,
        on_delete = models.CASCADE
    )
    commandeMedicament = models.ManyToManyField(
        Medicament,
    )
    commandeLivreur = models.ForeignKey(
        Livreur,
        on_delete= models.CASCADE
    )
    commandePharmacien = models.ForeignKey(
        Pharmacien,
        on_delete = models.CASCADE
    )

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