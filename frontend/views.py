from datetime import datetime
import json
from pyexpat.errors import messages
from django.http import Http404, HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.contrib.auth import login, logout
from django.contrib.auth.hashers import check_password
from gestionUtilisateurs.forms import ClientInscription, ConnexionForm, InscriptionForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from gestionStocks.models import *
from gestionUtilisateurs.models import *
from gestionVentes.forms import FormulaireCommandeForm
from gestionVentes.models import CommandePresentielle, Ordonnance, SelectionMedicament
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib import messages



# Début de la liste des Vues du template client

def about(request):
    return render(request, 'themes_client/about.html')

def cart(request):
    return render(request, 'themes_client/cart.html')

def checkout(request):
    return render(request, 'themes_client/checkout.html')

def contact(request):
    return render(request, 'themes_client/contact.html')

def shop_single(request):
    return render(request, 'themes_client/shop-single.html')

def shop(request):
    medicaments = Medicament.objects.all()
    categories = Categorie.objects.all()

    return render(request, 'themes_client/shop.html', {'medicaments':medicaments, 'categories':categories})

def thankyou(request):
    return render(request, 'themes_client/thankyou.html')



def redirection_commande(request):
    if request.session.get('user_email'):
        return redirect('commande_client')
    else:
        return redirect('inscription_client')

def commande_client(request):
    user_email = request.session.get('user_email')
    
    if user_email:
        try:
            client = Client.objects.get(emailUtilisateur=user_email)
        except Client.DoesNotExist:
            messages.error(request, 'Client non trouvé.')
            return redirect('inscription')
    else:
        messages.error(request, 'Utilisateur non authentifié.')
        return redirect('page_connexion')
    
    if request.method == 'POST':
        form = FormulaireCommandeForm(request.POST, request.FILES)
        if form.is_valid():
            # Créez une nouvelle ordonnance d'abord
            ordonnance = Ordonnance(
                image=form.cleaned_data['image'],
                ordonnance_client=client  # Associez l'ordonnance au client connecté
            )
            ordonnance.save()
            
            # Créez le formulaire de commande
            formulaire_commande = form.save(commit=False)
            formulaire_commande.ordonnance = ordonnance
            formulaire_commande.geolocalisation = form.cleaned_data['geolocalisation']  # Sauvegarder la géolocalisation
            formulaire_commande.save()
            
            return redirect('thankyou')  # Redirige vers une page de confirmation ou autre
    else:
        form = FormulaireCommandeForm()

    return render(request, 'themes_client/formulaire_commande.html', {'form': form})

def inscription_client(request):
    if request.method == 'POST':
        form = ClientInscription(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.set_password(form.cleaned_data['motDePasse'])
            client.save()
            return redirect('page_connexion')  # Remplacez 'accueil' par la redirection souhaitée
    else:
        form = ClientInscription()
    return render(request, 'themes_client/inscription_client.html', {'form': form})

#Fin de la liste des vues du template client

#Début de la liste des Vues du template admin


def homepage_prepa(request):
    return render(request, 'themes_admin/homepage_prepa.html')

def homepage_phar(request):
    return render(request, 'themes_admin/themes_pharmacien/homepage_phar.html')


def themes(request):
    return render(request, 'themes_admin/themes.html')



def edit_profile(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        first_name = request.POST.get('first_name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')
        user_email = request.session.get('user_email')

        if old_password and new_password:
            try:
                user = PreparateurEnPharmacie.objects.get(emailUtilisateur=user_email)
                if check_password(old_password, user.motDePasse):
                    user.nomUtilisateur = first_name
                    user.emailUtilisateur = email
                    user.numeroUtilisateur = mobile
                    user.adresseUtilisateur = address
                    user.set_password(new_password)
                    user.save()
                    messages.success(request, 'Profile updated successfully.')
                    return redirect('profil_utilisateur')  # Redirect to the same profile page after update
                else:
                    messages.error(request, 'Old password is incorrect.')
            except PreparateurEnPharmacie.DoesNotExist:
                messages.error(request, 'User does not exist.')
        else:
            messages.error(request, 'Please fill out both password fields.')

    user_info = {
        'name': request.session.get('user_name'),
        'email': request.session.get('user_email'),
        'mobile': request.session.get('user_numero'),
        'address': request.session.get('user_adresse'),
    }
    return render(request, 'themes_admin/edit_profile.html', user_info)
    
def edit_user(request):
    return render(request, 'themes_admin/edit_user.html')

def medicine_grid(request):
    medicaments = Medicament.objects.all()

    return render(request, 'themes_admin/medicine_grid.html', {'medicaments': medicaments})

def notification_date_expired(request):
    return render(request, 'themes_admin/notification_date_expired.html')

def notification_out_of_stock(request):
    return render(request, 'themes_admin/notification_out_of_stock.html')

def send_email(request):
    return render(request, 'themes_admin/send_email.html')

def user_activity(request):
    return render(request, 'themes_admin/user_activity.html')

def user_list(request):
    return render(request, 'themes_admin/user_list.html')

#Fin de la liste des vues du template admin

# Fonction de traitement de la création de catégorie
def creation_categorie(request):
    categorie = None
    error_message = None

    if request.method == 'POST':
        nomCat = request.POST.get('nomCat', '').strip()
        description = request.POST.get('description', '').strip()

        # Validate that both fields are non-empty and contain only alphabetic characters
        if not nomCat.isalpha():
            error_message = "Le nom de la catégorie doit contenir uniquement des lettres."
        elif not description.isalpha():
            error_message = "La description doit contenir uniquement des lettres."
        else:
            categorie = Categorie.objects.create(nomCat=nomCat, description=description)
            return redirect('liste_category')

    # Extraire les informations de l'utilisateur de la session
    user_name = request.session.get('user_name', 'Utilisateur')
    user_email = request.session.get('user_email', 'email@example.com')

    return render(request, "themes_admin/add_category.html", {'categories': categorie, 'error_message': error_message, 'user_name': user_name,
        'user_email': user_email,})




def creation_medicament(request):
    user_email = request.session.get('user_email')
    
    if user_email:
        try:
            preparateur = PreparateurEnPharmacie.objects.get(emailUtilisateur=user_email)
        except PreparateurEnPharmacie.DoesNotExist:
            # Redirigez ou affichez un message d'erreur si l'utilisateur n'est pas un préparateur en pharmacie
            return redirect('inscription')
        
        categories = Categorie.objects.all()
        today = datetime.today().date()

        if request.method == "POST":
            nomMedicament = request.POST['nomMedicament']
            libelle = request.POST['libelle']
            code = request.POST['code']
            prixUnitaire = request.POST['prixUnitaire']
            dateExpiration = request.POST['dateExpiration']
            image = request.FILES.get('image') if 'image' in request.FILES else None
            categorie_id = request.POST.get('nomCat')
            
            # Convertir la dateExpiration en objet date
            dateExpiration_obj = datetime.strptime(dateExpiration, '%Y-%m-%d').date()

            if dateExpiration_obj < today:
                return render(request, 'themes_admin/add_medicine.html', {
                    'categories': categories,
                    'today': today,
                    'error_message': 'La date d\'expiration ne peut pas être antérieure à aujourd\'hui.'
                })

            categorie = Categorie.objects.get(pk=categorie_id)

            medicament = Medicament(
                nomMedicament=nomMedicament,
                libelle=libelle,
                code=code,
                prixUnitaire=prixUnitaire,
                dateExpiration=dateExpiration,
                image=image,
                medicamentPreparateur=preparateur,
                medicamentCategorie=categorie,
            )
            medicament.save()
            return redirect('liste_medicaments')  # Redirigez vers une page de succès appropriée
        
        return render(request, 'themes_admin/add_medicine.html', {
            'categories': categories,
            'today': today
        })
    else:
        return redirect('page_connexion')

#Fonction d'affichage de la page de connexion
def page_connexion(request):
    if request.method == 'POST':
        form = ConnexionForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            motDePasse = form.cleaned_data['motDePasse']
            
            user = None
            user_models = [GestionnairePharmacie, PreparateurEnPharmacie, Caissier, Client, Pharmacien, Livreur]

            for user_model in user_models:
                try:
                    user = user_model.objects.get(emailUtilisateur=email)
                    if check_password(motDePasse, user.motDePasse):
                        login(request, user)
                        # Stocker les informations de l'utilisateur dans la session
                        request.session['user_email'] = user.emailUtilisateur
                        request.session['user_name'] = user.nomUtilisateur
                        request.session['user_prenom'] = user.prenomUtilisateur
                        request.session['user_numero'] = user.numeroUtilisateur
                        request.session['user_adresse'] = user.adresseUtilisateur
                        request.session['user_role'] = user.role
                        
                        if isinstance(user, Client):
                            return redirect('liste_medicaments_client')
                        elif isinstance(user, Pharmacien):
                            return redirect('homepage_phar')
                        elif isinstance(user, Caissier):
                            return redirect('afficher_medicaments_selectionnes')
                        else:
                            return redirect('homepage_prepa')
                    else:
                        form.add_error(None, "Email ou mot de passe incorrect.")
                        break
                except user_model.DoesNotExist:
                    continue

            if user is None:
                form.add_error(None, "Email ou mot de passe incorrect.")
    else:
        form = ConnexionForm()
    
    return render(request, 'themes_admin/login.html', {'form': form})

def inscription(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data['role']
            user_data = {
                'nomUtilisateur': form.cleaned_data['nomUtilisateur'],
                'prenomUtilisateur': form.cleaned_data['prenomUtilisateur'],
                'numeroUtilisateur': form.cleaned_data['numeroUtilisateur'],
                'adresseUtilisateur': form.cleaned_data['adresseUtilisateur'],
                'emailUtilisateur': form.cleaned_data['emailUtilisateur'],
                'role': role,
            }
            if role == 'GestionnairePharmacie':
                user = GestionnairePharmacie(**user_data)
            elif role == 'PreparateurEnPharmacie':
                user = PreparateurEnPharmacie(**user_data)
            elif role == 'Caissier':
                user = Caissier(**user_data)
            elif role == 'Client':
                user = Client(**user_data)
            elif role == 'Pharmacien':
                user = Pharmacien(**user_data)
            elif role == 'Livreur':
                user = Livreur(**user_data)

            user.set_password(form.cleaned_data['motDePasse'])
            user.save()
            return redirect('page_connexion')  # Rediriger vers la page de connexion après l'inscription
    else:
        form = InscriptionForm()
    return render(request, 'themes_admin/inscription.html', {'form': form})

def profil_utilisateur(request):
    user_info = {
        'name': request.session.get('user_name'),
        'prenom': request.session.get('user_prenom'),
        'email': request.session.get('user_email'),
        'numero': request.session.get('user_numero'),
        'adresse': request.session.get('user_adresse'),
        'role': request.session.get('user_role'),
    }
    return render(request, 'themes_admin/my_profile.html', user_info)

#Fonction d'affichage de catégorie
def liste_category(request):
    categories = Categorie.objects.all()
    return render(request, 'themes_admin/category_list.html', {'categories': categories})

    
#Fonction de suppression de catégorie :
def supprimer_categorie(request, categorie_id):
    if request.method == 'POST':
        categorie_id = request.POST.get('categorie_id')
        categorie = get_object_or_404(Categorie, pk=categorie_id)
        categorie.delete()
        return redirect('liste_category')
    return render(request, 'themes_admin/category_list.html')

#Fonction d'affichage de médicaments
def liste_medicaments(request):
    # Récupérer tous les médicaments avec leurs catégories associées
    medicaments = Medicament.objects.all()
    categories = Categorie.objects.all()

    return render(request, 'themes_admin/medicine_list.html', {'medicaments': medicaments, 'categories': categories})

# Fonction de suppression de médicament
def supprimer_medicament(request, medicament_id):
    if request.method == 'POST':
        medicament = get_object_or_404(Medicament, pk=medicament_id)
        medicament.delete()
        return redirect('liste_medicaments')
    return render(request, 'themes_admin/medicine_list.html')

def modifier_medicament(request, medicament_id):
    user_email = request.session.get('user_email')
    
    if user_email:
        try:
            preparateur = PreparateurEnPharmacie.objects.get(emailUtilisateur=user_email)
        except PreparateurEnPharmacie.DoesNotExist:
            # Redirigez ou affichez un message d'erreur si l'utilisateur n'est pas un préparateur en pharmacie
            return redirect('inscription')
        
        medicament = get_object_or_404(Medicament, pk=medicament_id)
        categories = Categorie.objects.all()

        if request.method == 'POST':
            nomMedicament = request.POST.get('nomMedicament')
            libelle = request.POST.get('libelle')
            code = request.POST.get('code')
            prixUnitaire = request.POST.get('prixUnitaire')
            dateExpiration = request.POST.get('dateExpiration')
            image = request.FILES.get('image')
            categorie_id = request.POST.get('nomCat')

            if nomMedicament:
                medicament.nomMedicament = nomMedicament
            if libelle:
                medicament.libelle = libelle
            if code:
                medicament.code = code
            if prixUnitaire:
                medicament.prixUnitaire = prixUnitaire
            if dateExpiration:
                medicament.dateExpiration = dateExpiration
            if image:
                medicament.image = image
            if categorie_id:
                categorie = Categorie.objects.get(pk=categorie_id)
                medicament.medicamentCategorie = categorie

            # Affecter le préparateur connecté au médicament
            medicament.medicamentPreparateur = preparateur

            medicament.save()

            return redirect('liste_medicaments')

        return render(request, "themes_admin/edit_medicine.html", {
            'medicament': medicament, 
            'categories': categories,
        })
    
def modifier_categorie(request, categorie_id):
    categorie = get_object_or_404(Categorie, pk=categorie_id)
    
    if request.method == 'POST':
        nomCat = request.POST.get('nomCat')
        description = request.POST.get('description')

        categorie.nomCat = nomCat
        categorie.description = description

        categorie.save()
        
        return redirect('liste_category')

    return render(request, "themes_admin/edit_category.html", {'categorie': categorie})


def show_details(request, id):
    medicament = get_object_or_404(Medicament, id=id)
    return render(request, 'themes_admin/show_details.html', {'medicament': medicament})

def liste_medicaments_client(request):
    # Récupérer tous les médicaments avec leurs catégories associées
    medicaments = Medicament.objects.all()
    categories = Categorie.objects.all()

    return render(request, 'themes_client/index.html', {'medicaments': medicaments, 'categories': categories})

def shop_single(request, medicament_id):
    medicament = get_object_or_404(Medicament, pk=medicament_id)
    return render(request, 'themes_client/shop-single.html', {'medicament': medicament})

def rechercher_medicament(request):
    query = request.GET.get('q', '')
    medicaments = Medicament.objects.filter(nomMedicament__icontains=query) | Medicament.objects.filter(medicamentCategorie__nomCat__icontains=query)
    return render(request, 'themes_client/index.html', {'medicaments': medicaments, 'query': query})

def formulaire_achat(request,ordonnance_id):
    ordonnance = get_object_or_404(Ordonnance, id=ordonnance_id)
    client = ordonnance.ordonnanceClient
    return render(request, 'themes_client/cart.html', {'client': client, 'ordonnance': ordonnance})



def pharamacien_listeMedicament(request):
    categories = Categorie.objects.prefetch_related('medicaments').all()
    user_name = request.session.get('user_name', 'Utilisateur')
    user_email = request.session.get('user_email', 'email@example.com')

    return render(request, 'themes_admin/themes_pharmacien/medicine_list.html', {'categories': categories, 'user_name': user_name,
        'user_email': user_email,})

  
def medicaments_selectionnés(request):
    user_email = request.session.get('user_email')
    
    if user_email:
        try:
            pharmacien = Pharmacien.objects.get(emailUtilisateur=user_email)
        except Pharmacien.DoesNotExist:
            messages.error(request, 'Pharmacien non trouvé.')
            return redirect('inscription')
    else:
        messages.error(request, 'Utilisateur non authentifié.')
        return redirect('page_connexion')

    if request.method == 'POST':
        selected_medicines_data = request.POST.get('selectedMedicinesData')
        selected_medicines = json.loads(selected_medicines_data)

        try:
            SelectionMedicament.objects.create(
                donnees=selected_medicines,
                pharmacien=pharmacien
            )
            messages.success(request, 'Données envoyées avec succès.')
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'enregistrement des données : {e}')

            return redirect('afficher_medicaments_selectionnes')
        
        return render(request, 'themes_admin/themes_pharmacien/medicine_list.html', {'message': 'Données envoyées avec succès.'})
    else:
        return render(request, 'themes_admin/themes_pharmacien/medicine_list.html', {'message': 'Invalid request method.'})
    
def journal_medicaments_selectionnes(request):   
    user_email = request.session.get('user_email')
    
    if user_email:
        try:
            pharmacien = Pharmacien.objects.get(emailUtilisateur=user_email)
        except Pharmacien.DoesNotExist:
            messages.error(request, 'Pharmacien non trouvé.')
            return redirect('inscription')
    else:
        messages.error(request, 'Utilisateur non authentifié.')
        return redirect('page_connexion')

    selections = SelectionMedicament.objects.filter(pharmacien=pharmacien).order_by('-dateCreation')
    
    return render(request, 'themes_admin/themes_pharmacien/commandes_list.html', {'selections': selections})
        
def afficher_medicaments_selectionnes(request):
    user_email = request.session.get('user_email')
    
    if user_email:
        try:
            caissier = Caissier.objects.get(emailUtilisateur=user_email)
        except Caissier.DoesNotExist:
            messages.error(request, 'Caissier non trouvé.')
            return redirect('inscription')
    else:
        messages.error(request, 'Utilisateur non authentifié.')
        return redirect('page_connexion')
    
    if request.method == 'POST':
        selection_id = request.POST.get('selection_id')
        total_price = request.POST.get('total_price')
        
        try:
            selection_medicaments = SelectionMedicament.objects.get(id=selection_id)
        except SelectionMedicament.DoesNotExist:
            messages.error(request, 'Médicaments sélectionnés non trouvés.')
            return redirect('some_error_page')

        # Convert total_price to integer before saving to the database
        total_price_int = int(float(total_price))

        # Créer une instance de CommandePresentielle
        CommandePresentielle.objects.create(
            prixTotal=total_price_int,
            selection_medicaments=selection_medicaments,
            caissier=caissier
        )
        
        selection_medicaments.etatDeValidation = True
        selection_medicaments.save()

        messages.success(request, 'Commande validée avec succès.')

    non_validated_medicines = SelectionMedicament.objects.filter(etatDeValidation=False).order_by('-id')
    
    context = {
        'non_validated_medicines': non_validated_medicines,
    }
    return render(request, 'themes_admin/themes_caissier/medicine_select.html', context)
        
def pharmacien_affichage_med(request):
    # Récupérer tous les médicaments avec leurs catégories associées
    medicaments = Medicament.objects.all()
    categories = Categorie.objects.all()

    return render(request, 'themes_admin/themes_pharmacien/affichage_med.html', {'medicaments': medicaments, 'categories': categories})

def pharmacien_affichage_med_grid(request):
    medicaments = Medicament.objects.all()

    return render(request, 'themes_admin/themes_pharmacien/affichage_med_grid.html', {'medicaments': medicaments})


def pharmacien_show_details(request, id):
    medicament = get_object_or_404(Medicament, id=id)
    return render(request, 'themes_admin/themes_pharmacien/show_details.html', {'medicament': medicament})

def deconnexion(request):
    logout(request)
    return redirect('liste_medicaments_client')