from datetime import timedelta
from django.db import models
from django.utils import timezone
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
    stock = models.PositiveIntegerField(default=0)

    medicamentPreparateur = models.ForeignKey(
        PreparateurEnPharmacie,
        on_delete=models.CASCADE
    )
    medicamentCategorie = models.ForeignKey(
        Categorie,  
        on_delete=models.RESTRICT,
        related_name='medicaments'
    )

    def calculer_prix_total(self, quantite):
        return self.prixUnitaire * quantite
    
    def verifier_reapprovisionnement(self, seuil=5):
        if self.stock <= seuil:
            return True  
        return False
    
    @classmethod
    def medicaments_expiration_proche(cls):
        actuel = timezone.now()
        une_semaine_avant = actuel + timedelta(weeks=1)
        return cls.objects.filter(dateExpiration__lte=une_semaine_avant, dateExpiration__gte=actuel)
    
    def deduire_stock(self, quantite):
        if self.stock >= quantite:
            self.stock -= quantite
            self.save()
        else:
            raise ValueError("Stock insuffisant")