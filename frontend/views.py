from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
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
from gestionVentes.forms import CommandeVirtuelleForm, DateRangeForm
from gestionVentes.models import CommandePresentielle, CommandeVirtuelle, Livraison, Ordonnance, SelectionMedicament
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib import messages
from django.views.decorators.http import require_POST



# Début de la liste des Vues du template client

def about(request):
    return render(request, 'themes_client/about.html')

def rapport(request):
    commandes_presentielles = CommandePresentielle.objects.all()
    commandes_virtuelles = CommandeVirtuelle.objects.all()
    total_commandes = CommandePresentielle.objects.count()
    total_valeur_commandes = CommandePresentielle.objects.aggregate(total=models.Sum('prixTotal'))['total'] or 0

    # Calcul du nombre total de produits débités du stock
    total_produits = 0
    for commande in commandes_presentielles:
        selection_donnees = commande.selection_medicaments.donnees
        if isinstance(selection_donnees, dict):  # Si c'est un dictionnaire
            total_produits += selection_donnees.get('quantite', 0)
        elif isinstance(selection_donnees, list):  # Si c'est une liste de dictionnaires
            for item in selection_donnees:
                total_produits += item.get('quantite', 0)

    form = DateRangeForm(request.GET or None)
    if form.is_valid():
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']

        if start_date == end_date:
            # Filtrer les commandes pour une date précise
            commandes_presentielles = commandes_presentielles.filter(date_validation=start_date)
        else:
            # Filtrer les commandes par intervalle de dates
            commandes_presentielles = commandes_presentielles.filter(date_validation__range=[start_date, end_date])

    context = {
        'commandes_presentielles': commandes_presentielles,
        'commandes_virtuelles': commandes_virtuelles,
        'total_commandes': total_commandes,
        'total_valeur_commandes': total_valeur_commandes,
        'total_produits': total_produits,
        'total_valeur_payee': 8500,  # Garder la valeur actuelle
        'form': form,  # Passer le formulaire au template
    }
    return render(request, 'themes_admin/themes_gestionnaire/invoice_report.html', context)


def liste_utilisateur_ges(request):
    gestionnaires = GestionnairePharmacie.objects.all()
    context = {
        'gestionnaires': gestionnaires,
    }
    return render(request, 'themes_admin/themes_gestionnaire/user_list.html', context)


def liste_utilisateur_prepa(request):
    preparateurs = PreparateurEnPharmacie.objects.all()
    context = {
        'preparateurs': preparateurs,
    }
    return render(request, 'themes_admin/themes_gestionnaire/user_list_prepa.html', context)

def liste_utilisateur_cas(request):
    caissiers = Caissier.objects.all()
    context = {
        'caissiers': caissiers,
    }
    return render(request, 'themes_admin/themes_gestionnaire/user_list_cas.html', context)

def liste_utilisateur_phar(request):
    pharmaciens = Pharmacien.objects.all()
    context = {
        'pharmaciens': pharmaciens,
    }
    return render(request, 'themes_admin/themes_gestionnaire/user_list_phar.html', context)

def liste_utilisateur_liv(request):
    livreurs = Livreur.objects.all()
    context = {
        'livreurs': livreurs,
    }
    return render(request, 'themes_admin/themes_gestionnaire/user_list_liv.html', context)

def liste_utilisateur_client(request):
    clients = Client.objects.all()
    context = {
        'clients': clients,
    }
    return render(request, 'themes_admin/themes_gestionnaire/user_list_client.html', context)



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

    # Récupérer la dernière ordonnance associée au client
    last_ordonnance = Ordonnance.objects.filter(ordonnance_client=client).order_by('-id').first()

    # Initialiser les variables
    selected_medicines = []
    selected_total = 0

    if last_ordonnance:
        # Filtrer les commandes virtuelles basées sur la dernière ordonnance
        accepted_order = CommandeVirtuelle.objects.filter(
            ordonnance=last_ordonnance,
            etat_validation=True
        ).order_by('-date_commande').first()
        
        refused_order = CommandeVirtuelle.objects.filter(
            ordonnance=last_ordonnance,
            etat_validation=False
        ).order_by('-date_commande').first()

        if accepted_order:
            for selection in accepted_order.ordonnance.selections.filter(statut='virtuelle', etatOrdonnance=True):
                # Extraire les données du JSONField (supposé être une liste)
                for item in selection.donnees:
                    med_id = item.get('id')
                    quantity = item.get('quantite', 1)
                    
                    try:
                        medicament = Medicament.objects.get(id=med_id)
                        total = medicament.prixUnitaire * quantity
                        selected_medicines.append({
                            'nom': medicament.nomMedicament,
                            'prix': medicament.prixUnitaire,
                            'quantite': quantity,
                            'total': total
                        })
                        selected_total += total
                    except Medicament.DoesNotExist:
                        continue  # Ignore les médicaments non trouvés

    context = {
        'commande_acceptee': accepted_order is not None,
        'selected_medicines': selected_medicines,
        'selected_total': selected_total,
        'commande_refusee': refused_order is not None,
        'refused_order': refused_order,
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

def homepage_liv(request):
    return render(request, 'themes_admin/themes_livreur/homepage_liv.html')

def homepage_ges(request):
    return render(request, 'themes_admin/themes_gestionnaire/homepage_ges.html')




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
    medicaments_proches = Medicament.medicaments_expiration_proche()
    context = {
        'medicaments': medicaments_proches,
    }
    return render(request, 'themes_admin/notification_date_expired.html', context)

def notification_out_of_stock(request):
    medicaments_reappro = Medicament.objects.filter(stock__lte=5)  
    context = {
        'medicaments': medicaments_reappro,
    }
    return render(request, 'themes_admin/notification_out_of_stock.html', context)

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
        elif not all(c.isalpha() or c.isspace() for c in description):
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
            stock = request.POST['stock']
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
                stock=stock,
                code=code,
                prixUnitaire=prixUnitaire,
                dateExpiration=dateExpiration,
                image=image,
                medicamentPreparateur=preparateur,
                medicamentCategorie=categorie,
            )
            medicament.save()
            return redirect('liste_medicaments')  
        
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
                        request.session['user_email'] = user.emailUtilisateur
                        request.session['user_name'] = user.nomUtilisateur
                        request.session['user_prenom'] = user.prenomUtilisateur
                        request.session['user_numero'] = user.numeroUtilisateur
                        request.session['user_adresse'] = user.adresseUtilisateur
                        request.session['user_role'] = user.role
                        
                        if isinstance(user, GestionnairePharmacie):
                            return redirect('homepage_ges')
                        elif isinstance(user, Pharmacien):
                            return redirect('homepage_phar')
                        elif isinstance(user, Caissier):
                            return redirect('homepage_car')
                        elif isinstance(user, Livreur):
                            return redirect('homepage_liv')
                        elif isinstance(user, PreparateurEnPharmacie):
                            return redirect('homepage_prepa')
                        else:
                            return redirect('liste_medicaments_client')
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
            stock = request.POST.get('stock')
            code = request.POST.get('code')
            prixUnitaire = request.POST.get('prixUnitaire')
            dateExpiration = request.POST.get('dateExpiration')
            image = request.FILES.get('image')
            categorie_id = request.POST.get('nomCat')

            if nomMedicament:
                medicament.nomMedicament = nomMedicament
            if libelle:
                medicament.libelle = libelle
            if stock:
                medicament.stock = stock
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

def creer_commande(request):
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

    ordonnance_details = None 
    ordonnance_details = request.session.pop('ordonnance_details', None)
    
    if request.method == 'POST':
        statut_commande = request.POST.get('statutCommandeHidden')
        medicaments = request.POST.get('medicaments', '[]')
        ordonnance_id = request.POST.get('ordonnance_id', None)

        if ordonnance_id:   
            ordonnance_details = get_object_or_404(Ordonnance, id=ordonnance_id)

        try:
            medicaments_data = json.loads(medicaments)
            total_price = sum(int(med['prix_total']) for med in medicaments_data)
            
            # Gestion du stock
            for med in medicaments_data:
                medicament = Medicament.objects.get(nomMedicament=med['nom'])
                if medicament.stock >= med['quantite']:
                    medicament.stock -= med['quantite']
                    medicament.save()
                else:
                    messages.error(request, f"Stock insuffisant pour le médicament {med['nom']}.")
                    return redirect('journal_medicaments_selectionnes')

            # Créer la commande avec l'ordonnance et le statut correctement associés
            selection_medicament = SelectionMedicament.objects.create(
                etatOrdonnance=True,
                statut=statut_commande,
                donnees=medicaments_data,
                ordonnance=ordonnance_details,
                pharmacien=pharmacien
            )
            selection_medicament.save()
            
            # Stocker le prix total dans la session
            if 'commandes_totals' not in request.session:
                request.session['commandes_totals'] = {}
            request.session['commandes_totals'][str(selection_medicament.id)] = total_price
            request.session.modified = True
            request.session['ordonnance_id'] = ordonnance_id
            
            messages.success(request, "La commande a été créée avec succès.")
            return redirect('journal_medicaments_selectionnes')
        
        except Exception as e:
            # Handle errors
            messages.error(request, f"Erreur lors de la création de la commande: {str(e)}")
            return redirect('journal_medicaments_selectionnes')
    
    return render(request, 'themes_admin/themes_pharmacien/page1.html', {'ordonnance_details': ordonnance_details})

def recherche_medicament(request):
    query = request.GET.get('query', '')
    if query:
        # Rechercher les médicaments par nom ou code qui contiennent la chaîne de requête
        medicaments = Medicament.objects.filter(
            Q(nomMedicament__icontains=query) | Q(code__icontains=query)
        )
        # Format des données à retourner au format JSON
        medicament_data = [
            {
                'id': medicament.id,
                'code': medicament.code,
                'nom': medicament.nomMedicament,
                'prix': medicament.prixUnitaire,
            } for medicament in medicaments
        ]
    else:
        medicament_data = []

    return JsonResponse(medicament_data, safe=False)

def pharamacien_listeMedicament(request):
    categories = Categorie.objects.prefetch_related('medicaments').all()
    user_name = request.session.get('user_name', 'Utilisateur')
    user_email = request.session.get('user_email', 'email@example.com')

    ordonnance_details = request.session.pop('ordonnance_details', None)

    # Choisir le template en fonction du chemin de la requête
    if request.path == '/pharmacien/listeMedicaments':
        template_name = 'themes_admin/themes_pharmacien/medicine_list.html'
    elif request.path == '/pharmacien/page1':
        template_name = 'themes_admin/themes_pharmacien/page1.html'
    else:
        template_name = 'themes_admin/themes_pharmacien/medicine_list.html'

    return render(request, template_name, {'categories': categories, 'user_name': user_name,
        'user_email': user_email, 'ordonnance_details': ordonnance_details})

  

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
            return redirect('details_livraison_client')
        
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

    # Récupérer les prix totaux depuis la session
    commandes_totals = request.session.get('commandes_totals', {})

    return render(request, 'themes_admin/themes_pharmacien/commandes_list.html', {'selections': selections, 'commandes_totals': commandes_totals})
        
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

    # Filtrer les commandes virtuelles avec etatOrdonnance=True et etatDeValidation=False
    virtual_orders = SelectionMedicament.objects.filter(
        etatOrdonnance=True,
        etatDeValidation=False
    ).exclude(
        statut='presentiel'
    ).order_by('-dateCreation')

    presencial_orders = SelectionMedicament.objects.filter(
            etatDeValidation=False,
            statut='presentiel'
        ).order_by('-id')

    context = {
        'virtual_orders': virtual_orders,
        'presencial_orders': presencial_orders
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

    return redirect('creer_commande')

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
        

        return redirect('pharmacien_commandeVirtuelle', commande_id=commande.id)
    
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
    livreurs = Livreur.objects.all()
    context = {
        'selections': selections,
        'livreurs': livreurs,
    }
    return render(request, 'themes_admin/themes_caissier/commande_liste.html', context)

def assigner_livreur(request):
    if request.method == 'POST':
        selection_id = request.POST.get('selection_id')
        livreur_id = request.POST.get('livreur')

        try:
            selection = SelectionMedicament.objects.get(id=selection_id)
            if not selection.ordonnance:
                messages.error(request, "Aucune ordonnance associée à cette sélection.")
                return redirect('caissier_commandes_validees')

            ordonnance = selection.ordonnance
            livreur = Livreur.objects.get(id=livreur_id)
            livraison, created = Livraison.objects.get_or_create(ordonnance=ordonnance, defaults={'livreur': livreur})

            if not created:
                livraison.livreur = livreur
                livraison.save()

            messages.success(request, 'Livreur assigné avec succès.')
        except (SelectionMedicament.DoesNotExist, Livreur.DoesNotExist):
            messages.error(request, "Erreur lors de l'assignation du livreur.")

    return redirect('caissier_commandes_validees')

def liste_livraisons_livreur(request):
    user_email = request.session.get('user_email')
    
    if user_email:
        try:
            livreur = Livreur.objects.get(emailUtilisateur=user_email)
        except Livreur.DoesNotExist:
            messages.error(request, 'Livreur non trouvé.')
            return redirect('page_connexion')
    else:
        messages.error(request, 'Utilisateur non authentifié.')
        return redirect('page_connexion')

    livraisons = Livraison.objects.filter(livreur=livreur)
    
    context = {
        'livraisons': livraisons,
    }
    return render(request, 'themes_admin/themes_livreur/liste_livraison.html', context)

def details_livraison_client(request):

    user_email = request.session.get('user_email')

    if not user_email:
        messages.error(request, 'Utilisateur non authentifié.')
        return redirect('page_connexion')

    try:
        client = Client.objects.get(emailUtilisateur=user_email)
    except Client.DoesNotExist:
        messages.error(request, 'Client non trouvé.')
        return redirect('inscription_client')

    try:
        dernier_ordonnance = Ordonnance.objects.filter(ordonnance_client=client).latest('id')
    except Ordonnance.DoesNotExist:
        messages.warning(request, 'Aucune ordonnance trouvée pour ce client.')
        return redirect('page_connexion')

    livraisons = Livraison.objects.filter(ordonnance=dernier_ordonnance)

    if request.method == 'POST':
        livraison_id = request.POST.get('livraison_id')
        livraison = get_object_or_404(Livraison, id=livraison_id)

        if livraison.ordonnance == dernier_ordonnance:
            livraison.etat_de_livraison = True
            livraison.date_validation = timezone.now()
            livraison.save()
            return redirect('details_livraison_client')

    context = {
        'livraisons': livraisons,
        'livraison_validée': any(livraison.etat_de_livraison for livraison in livraisons),
    }

    return render(request, 'themes_client/details_livraison.html', context)

def historique_commandes_client(request):
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

    # Récupérer toutes les ordonnances validées associées à ce client
    ordonnances_validées = Ordonnance.objects.filter(ordonnance_client=client, livraison__etat_de_livraison=True).distinct()

    context = {
        'ordonnances_validées': ordonnances_validées,
    }
    return render(request, 'themes_client/historique_commandes.html', context)

