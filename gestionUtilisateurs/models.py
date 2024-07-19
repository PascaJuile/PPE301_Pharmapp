from django.db import models
from django.contrib.auth.hashers import make_password

class Utilisateur(models.Model):
    nomUtilisateur = models.CharField(max_length=100)
    prenomUtilisateur = models.CharField(max_length=150)
    numeroUtilisateur = models.IntegerField()
    adresseUtilisateur = models.CharField(max_length=255)
    emailUtilisateur = models.EmailField(unique=True)
    motDePasse = models.CharField(max_length=100)
    role = models.CharField(max_length=150, default="utilisateur")
    last_login = models.DateTimeField(null=True, blank=True)  

    class Meta:
        abstract = True

    def set_password(self, raw_password):
        self.motDePasse = make_password(raw_password)

class GestionnairePharmacie(Utilisateur):
    pass

class PreparateurEnPharmacie(Utilisateur):
    pass

class Caissier(Utilisateur):
    pass

class Client(Utilisateur):
    pass

class Pharmacien(Utilisateur):
    pass

class Livreur(Utilisateur):
    pass