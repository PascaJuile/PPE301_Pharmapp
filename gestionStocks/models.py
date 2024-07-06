from django.db import models
from gestionUtilisateurs.models import PreparateurEnPharmacie

class Categorie(models.Model):
    nomCat = models.CharField(max_length=100)
    description = models.CharField(max_length=255)

class Medicament(models.Model):
    nomMedicament = models.CharField(max_length=150)
    libelle = models.CharField(max_length=255)  
    code = models.CharField(max_length=100)     
    prixUnitaire = models.IntegerField()
    dateExpiration = models.DateTimeField()
    image = models.ImageField(upload_to='medicament_images/', null=True, blank=True)

    medicamentPreparateur = models.ForeignKey(
        PreparateurEnPharmacie,
        on_delete=models.CASCADE
    )
    medicamentCategorie = models.ForeignKey(
        Categorie,  
        on_delete=models.RESTRICT,
        related_name='medicaments'
    )
