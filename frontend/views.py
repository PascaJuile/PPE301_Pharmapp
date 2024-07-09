from pyexpat.errors import messages
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.contrib.auth import authenticate, login
from .form import LoginForm

from gestionStocks.models import *
from gestionUtilisateurs.models import *


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
    return render(request, 'themes_client/shop.html')

def thankyou(request):
    return render(request, 'themes_client/thankyou.html')

#Fin de la liste des vues du template client

#Début de la liste des Vues du template admin

def login(request):
    return render(request, 'themes_admin/login.html')

def add_category(request):
    print("super 2")
    return render(request, 'themes_admin/add_category.html')

def themes(request):
    return render(request, 'themes_admin/themes.html')

def add_medicine(request):
    return render(request, 'themes_admin/add_medicine.html')

def edit_profile(request):
    return render(request, 'themes_admin/edit_profile.html')

def edit_user(request):
    return render(request, 'themes_admin/edit_user.html')

def medicine_grid(request):
    return render(request, 'themes_admin/medicine_grid.html')

def my_profile(request):
    return render(request, 'themes_admin/my_profile.html')

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

    return render(request, "themes_admin/add_category.html", {'categories': categorie, 'error_message': error_message})

#Fonction de création de médicament  
def creation_medicament(request):
    if request.method == "POST":
        nomMedicament = request.POST['nomMedicament']
        libelle = request.POST['libelle']
        code = request.POST['code']
        prixUnitaire = request.POST['prixUnitaire']
        dateExpiration = request.POST['dateExpiration']
        image = request.FILES.get('image') if 'image' in request.FILES else None
        categorie_id = request.POST.get('nomCat')
        preparateur_id = request.POST.get('preparateur')
        
        preparateur = PreparateurEnPharmacie.objects.get(pk=preparateur_id)
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
    
    preparateurs = PreparateurEnPharmacie.objects.all()
    categories = Categorie.objects.all()

    return render(request, 'themes_admin/add_medicine.html', {'categories': categories, 'preparateurs': preparateurs})

#Fonction d'affichage de la page de connexion
def page_connexion(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # Perform login logic here
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # Authenticate and login user here
            return redirect('creation_categorie')  # Redirect to a success page
    else:
        form = LoginForm()
    return render(request, 'themes_admin/login.html', {'form': form})
    

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
    medicament = get_object_or_404(Medicament, pk=medicament_id)
    categories = Categorie.objects.all()
    preparateurs = PreparateurEnPharmacie.objects.all()

    if request.method == 'POST':
        nomMedicament = request.POST.get('nomMedicament')
        libelle = request.POST.get('libelle')
        code = request.POST.get('code')
        prixUnitaire = request.POST.get('prixUnitaire')
        dateExpiration = request.POST.get('dateExpiration')
        image = request.FILES.get('image')
        categorie_id = request.POST.get('nomCat')
        preparateur_id = request.POST.get('preparateur')

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
            medicament.categorie_id = categorie_id
        if preparateur_id:
            medicament.preparateur_id = preparateur_id

        medicament.save()

        return redirect('liste_medicaments')

    return render(request, "themes_admin/edit_medicine.html", {'medicament': medicament, 'categories': categories, 'preparateurs': preparateurs})

def show_details(request, id):
    medicament = get_object_or_404(Medicament, id=id)
    return render(request, 'themes_admin/show_details.html', {'medicament': medicament})

def liste_medicaments_client(request):
    # Récupérer tous les médicaments avec leurs catégories associées
    medicaments = Medicament.objects.all()
    categories = Categorie.objects.all()

    return render(request, 'themes_client/index.html', {'medicaments': medicaments, 'categories': categories})
