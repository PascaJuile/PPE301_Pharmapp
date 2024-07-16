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


class Commande(models.Model):
    prixTotal= models.IntegerField()
    dateCommande = models.DateTimeField()
    etatDeCommande = models.BooleanField()
    etatDeLivraison = models.BooleanField()

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