
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
from gestionVentes.forms import CommandeVirtuelleForm
from gestionVentes.models import CommandePresentielle, CommandeVirtuelle, Ordonnance, SelectionMedicament
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib import messages



# Début de la liste des Vues du template client

def about(request):
    return render(request, 'themes_client/about.html')

def cart(request):
    user_email = request.session.get('user_email')
    
    if user_email:
        try:
            client = Client.objects.get(emailUtilisateur=user_email)
        except Client.DoesNotExist:
            messages.error(request, 'Client non trouvé.')
            return redirect('inscription_client')
    else:
        messages.error(request, 'Utilisateur non authentifié.')
        return redirect('page_connexion')

    # Récupérer les données de la session
    selected_medicines = request.session.get('selected_medicines')
    selected_total = request.session.get('selected_total')
    refus_motif = request.session.get('refus_motif')
    ordonnance_id = request.session.get('ordonnance_id')  # Récupérer l'ID de l'ordonnance

    # Si ordonnance_id n'est pas dans la session, récupérez-le depuis le modèle Ordonnance
    if not ordonnance_id:
        try:
            # Filtrer les ordonnances associées au client et prendre la première
            ordonnance = Ordonnance.objects.filter(ordonnance_client=client).last()
            if ordonnance:
                ordonnance_id = ordonnance.id
                # Ajouter ordonnance_id à la session pour un accès ultérieur
                request.session['ordonnance_id'] = ordonnance_id
            else:
                ordonnance_id = None
                messages.error(request, 'Aucune ordonnance associée au client.')
        except Ordonnance.DoesNotExist:
            ordonnance_id = None
            messages.error(request, 'Aucune ordonnance associée au client.')

    # Déterminer l'état de la commande (acceptée ou refusée)
    if selected_medicines and selected_total:
        context = {
            'commande_acceptee': True,
            'selected_medicines': selected_medicines,
            'selected_total': selected_total,
            'ordonnance_id': ordonnance_id,  # Ajouter l'ID de l'ordonnance au contexte
        }
    elif refus_motif:
        context = {
            'commande_refusee': True,
            'refus_motif': refus_motif,
        }
    else:
        context = {
            'commande_acceptee': False,
            'commande_refusee': False,
        }
    
    return render(request, 'themes_client/cart.html', context)

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
            return redirect('inscription_client')
    else:
        messages.error(request, 'Utilisateur non authentifié.')
        return redirect('page_connexion')
    
    if request.method == 'POST':
        form = CommandeVirtuelleForm(request.POST, request.FILES)
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
        form = CommandeVirtuelleForm()

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

def homepage_car(request):
    return render(request, 'themes_admin/themes_caissier/homepage_car.html')


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

    ordonnance_details = request.session.pop('ordonnance_details', None)

    return render(request, 'themes_admin/themes_pharmacien/medicine_list.html', {'categories': categories, 'user_name': user_name,
        'user_email': user_email, 'ordonnance_details': ordonnance_details})

  
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
        selected_statut = request.POST.get('selectedMedicinesStatut')
        selected_total = request.POST.get('selectedMedicinesTotal')
        ordonnance_id = request.POST.get('ordonnance_id', None)

        ordonnance = None
        if ordonnance_id:   
            ordonnance = get_object_or_404(Ordonnance, id=ordonnance_id)

        try:
            SelectionMedicament.objects.create(
                donnees=selected_medicines,
                statut=selected_statut,
                pharmacien=pharmacien,
                ordonnance=ordonnance  # Assigner l'ordonnance récupérée
            )

            
            request.session['selected_medicines'] = selected_medicines
            request.session['selected_total'] = sum(int(med['prix']) * int(med['quantite']) for med in selected_medicines)
            request.session['ordonnance_id'] = request.POST.get('ordonnance_id')

            messages.success(request, 'Médicaments sélectionnés enregistrés avec succès.')
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'enregistrement des données : {e}')
            return redirect('journal_medicaments_selectionnes')

        return redirect('journal_medicaments_selectionnes')
    else:
        return render(request, 'themes_admin/themes_pharmacien/medicine_list.html', {'message': 'Invalid request method.'})    

def payement_commande(request):
    if request.method == "POST":
        mode_paiement = request.POST.get('mode_paiement')
        password = request.POST.get('password')
        ordonnance_id = request.POST.get('ordonnance_id')  # Récupérer l'ID de l'ordonnance à partir du formulaire POST

        # Debugging: Check received POST data
        print(f"Mode de paiement: {mode_paiement}")
        print(f"Mot de passe: {password}")
        print(f"Ordonnance ID: {ordonnance_id}")

        if ordonnance_id:
            try:
                commande = get_object_or_404(CommandeVirtuelle, ordonnance_id=ordonnance_id)
                print(f"Commande trouvée: {commande}")
                
                # Update the payment status
                commande.etat_payement = True
                commande.mode_paiement = mode_paiement
                commande.save()
                print(f"Commande mise à jour: {commande.etat_payement}, {commande.mode_paiement}")
                
                # Effacer les données de la session
                request.session.pop('selected_medicines', None)
                request.session.pop('selected_total', None)
                request.session.pop('ordonnance_id', None)
                
                # Ajouter un message de succès
                messages.success(request, 'Votre paiement a été traité avec succès. Merci pour votre commande!')
            except Exception as e:
                # Log any exceptions
                print(f"Erreur lors de la mise à jour de la commande: {e}")
                messages.error(request, 'Une erreur est survenue lors du traitement de votre paiement.')

            # Rediriger vers la page du panier (ou une autre page appropriée)
            return redirect('cart')
        
    return render(request, "themes_client/cart.html")
                
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

    non_validated_medicines = SelectionMedicament.objects.filter(
            etatDeValidation=False
        ).exclude(
            statut='virtuelle', 
            ordonnance__commandevirtuelle__etat_payement=False
        ).order_by('-id')    
    context = {
        'non_validated_medicines': non_validated_medicines,
    }
    return render(request, 'themes_admin/themes_caissier/medicine_select.html', context)

def pharmacien_commandeVirtuelle(request, commande_id):
    commande = get_object_or_404(CommandeVirtuelle, id=commande_id)
    return render(request, 'themes_admin/themes_pharmacien/commande_virtuelle.html', {'commande': commande})

def liste_commandes_virtuelles(request):
    commandes = CommandeVirtuelle.objects.all()
    return render(request, 'themes_admin/themes_pharmacien/liste_commandes_virtuelles.html', {'commandes': commandes})

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

def accepter_commande(request, commande_id):
    commande = get_object_or_404(CommandeVirtuelle, id=commande_id)
    commande.accepter_commande()
    messages.success(request, 'L\'ordonnance a été acceptée.')

    # Redirect with ordonnance details
    ordonnance_details = {
        'id': commande.ordonnance.id,
        'image_url': commande.ordonnance.image.url,
        'nom': commande.ordonnance.ordonnance_client.nomUtilisateur,
        'contact': commande.ordonnance.ordonnance_client.numeroUtilisateur,
    }

    request.session['ordonnance_details'] = ordonnance_details

    return redirect('pharamacien_listeMedicament')

def affichage_commande_acceptee(request, commande_id):
    try:
        commande = CommandePresentielle.objects.get(id=commande_id)
        request.session['commande_status'] = 'accepted'
        request.session['selected_medicines'] = commande.selected_medicines
        request.session['selected_total'] = commande.total_price
        messages.success(request, 'Commande acceptée avec succès.')
    except CommandePresentielle.DoesNotExist:
        messages.error(request, 'Commande non trouvée.')
    
    return redirect('cart')

def refuser_commande(request, commande_id):
    if request.method == 'POST':
        commande = CommandeVirtuelle.objects.get(id=commande_id)
        motif = request.POST.get('motif')
        commande.motif = motif
        commande.save()
        
        request.session['refus_motif'] = motif
        request.session['commande_image'] = commande.ordonnance.image.url 

        return redirect('cart')

    return HttpResponse(status=405)


  
def deconnexion(request):
    logout(request)
    return redirect('liste_medicaments_client')


def delete_order(request, pk):
    selection = get_object_or_404(SelectionMedicament, pk=pk)
    
    if not selection.etatDeValidation:
        selection.delete()
        messages.success(request, 'Commande supprimée avec succès.')
    else:
        messages.error(request, 'Impossible de supprimer une commande validée.')
    
    return redirect('journal_medicaments_selectionnes')

def caissier_commandes_validees(request):
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
    
    selections = SelectionMedicament.objects.filter(etatDeValidation=True)
    context = {
        'selections': selections,
    }
    return render(request, 'themes_admin/themes_caissier/commande_liste.html', context)
