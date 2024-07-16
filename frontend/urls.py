from . import views
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    #Liste des paths du template client
    path('about', views.about, name='about'),
    path('cart', views.cart, name='cart'),
    path('checkout', views.checkout, name='checkout'),
    path('shop_single', views.shop_single, name='shop_single'),
    path('contact', views.contact, name='contact'),
    path('shop', views.shop, name='shop'),
    path('thankyou', views.thankyou, name='thankyou'),
    #path d'affichage de la liste des médicament
    path('acceuil', views.liste_medicaments_client, name='liste_medicaments_client'),
    #path pour affichifer les infos d'un médicament
    path('shop_single/<int:medicament_id>/', views.shop_single, name='shop_single'),
    #path de recherche de médicament par son nom ou sa catégorie
    path('rechercher_medicament', views.rechercher_medicament, name='rechercher_medicament'),
    #path de scanne de l'ordonnance
    path('upload_ordonnance', views.upload_ordonnance, name='upload_ordonnance'),
    #path du formulaire d'achat pour chaque med
    #path('shop_single/<int:pk>/formulaire_achat/', views.formulaire_achat, name='formulaire_achat'),
    #path du formulaire d'achat
    path('formulaire_achat/<int:ordonnance_id>/', views.formulaire_achat, name='formulaire_achat'),
    path('formulaire_achat/<int:ordonnance_id>/', views.formulaire_achat, name='formulaire_achat'),




    #Liste des paths du template admin
    path('login', views.login, name='login'),
    #path('category', views.add_category, name='add_category'),
    path('themes', views.themes, name='themes'),
    path('edit_profile', views.edit_profile, name='edit_profile'),
    path('edit_user', views.edit_user, name='edit_user'),
    #path('add_medicine', views.add_medicine, name='add_medicine'),
    path('medicine_grid', views.medicine_grid, name='medicine_grid'),
    path('my_profile', views.my_profile, name='my_profile'),
    path('notification_expired', views.notification_date_expired, name='notification_date_expired'),
    path('notification_out_stock', views.notification_out_of_stock, name='notification_out_of_stock'),
    path('email', views.send_email, name='send_email'),
    path('user_activity', views.user_activity, name='user_medicine'),
    path('user_list', views.user_list, name='user_list'),
    #path de création de catégorie
    path('category_creation', views.creation_categorie, name='creation_categorie'),
    #path de création de médicament
    path('medicament_creation', views.creation_medicament, name='creation_medicament'),
    #path de création de la login page
    path('page_connexion', views.page_connexion, name='page_connexion'),
    #path de la page d'inscription
    path('', views.inscription, name='inscription'),
    #path d'affichage de la catégorie
    path('category_affichage', views.liste_category, name='liste_category'),
    #path de suppression de la catégorie
    path('supprimer_categorie/<int:categorie_id>/', views.supprimer_categorie, name='supprimer_categorie'),
    #path de suppression de médicament
    path('supprimer_medicament/<int:medicament_id>/', views.supprimer_medicament, name='supprimer_medicament'),
    #path de modification de médicament
    path('modifier_medicament/<int:medicament_id>/', views.modifier_medicament, name='vmodifier_medicament'),
    #path de modification de catégorie
    path('modifier_categorie/<int:categorie_id>/', views.modifier_categorie, name='vmodifier_categorie'),
    #path d'affichage de la liste de médicaments
    path('liste_medicaments', views.liste_medicaments, name='liste_medicaments'),
    #path d'affichage des détails d'un médicament
    path('show_details/<int:id>/', views.show_details, name='show_details'),


    
    #PATH DU PHARMACIEN
    path('listeMedicaments', views.pharamacien_listeMedicament, name='pharamacien_listeMedicament'),
    path('medicaments_selectionnes', views.medicaments_selectionnes, name='medicaments_selectionnes'),
    path('affichage_medicament_selectionnes', views.affichage_medicament_selectionnes, name='affichage_medicament_selectionnes'),



]   + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

