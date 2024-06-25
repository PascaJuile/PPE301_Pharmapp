from pyexpat.errors import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from gestionStocks.models import *

# Début de la liste des Vues du template client
def index(request):
    return render(request, 'themes_client/index.html')

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
    return render(request, 'themes_admin/add_category.html')

def themes(request):
    return render(request, 'themes_admin/themes.html')

def add_medicine(request):
    return render(request, 'themes_admin/add_medicine.html')

def category_list(request):
    return render(request, 'themes_admin/category_list.html')

def edit_profile(request):
    return render(request, 'themes_admin/edit_profile.html')

def edit_user(request):
    return render(request, 'themes_admin/edit_user.html')

def medicine_grid(request):
    return render(request, 'themes_admin/medicine_grid.html')

def medicine_list(request):
    return render(request, 'themes_admin/medicine_list.html')

def my_profile(request):
    return render(request, 'themes_admin/my_profile.html')

def notification_date_expired(request):
    return render(request, 'themes_admin/notification_date_expired.html')

def notification_out_of_stock(request):
    return render(request, 'themes_admin/notification_out_of_stock.html')

def send_email(request):
    return render(request, 'themes_admin/send_email.html')

def show_batch(request):
    return render(request, 'themes_admin/show_batch.html')

def show_details_setamol(request):
    return render(request, 'themes_admin/show_details_setamol.html')

def user_activity(request):
    return render(request, 'themes_admin/user_activity.html')

def user_list(request):
    return render(request, 'themes_admin/user_list.html')

#Fin de la liste des vues du template admin

#Fonction de traitement de la création de catégorie
def creation_categorie(request):
    if request.method == 'POST':
        nomCat = request.POST.get('nomCat', '')  
        description = request.POST.get('description', '')
       
        categorie = Categorie.objects.create(nom_cat=nomCat, description=description)

        redirect('liste_category')  

    return render(request, "add_category.html", {'categories':categorie})
    
def liste_category(request):
    categories = Categorie.objects.all()
    return render(request, 'category_list.html', {'categories': categories})

    
