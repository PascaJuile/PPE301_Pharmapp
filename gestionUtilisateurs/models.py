from django.db import models

class Utilisateur(models.Model):
    nomUtilisateur = models.CharField(max_length=100)
    prenomUtilisateur = models.CharField(max_length=150)
    numeroUtilisateur = models.IntegerField()
    adresseUtilisateur = models.CharField(max_length=255)
    emailUtilisateur = models.EmailField()
    motDePasse = models.CharField(max_length=100)
    role = models.CharField(max_length=150, default="utilisateur")
    class Meta:
        abstract = True

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
