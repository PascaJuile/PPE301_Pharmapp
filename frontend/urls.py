from . import views
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    #Liste des paths du template client
    #path('', views.index, name='index'),
    path('about', views.about, name='about'),
    path('cart', views.cart, name='cart'),
    path('checkout', views.checkout, name='checkout'),
    path('shop_single', views.shop_single, name='shop_single'),
    path('contact', views.contact, name='contact'),
    path('shop', views.shop, name='shop'),
    path('thankyou', views.thankyou, name='thankyou'),


    #Liste des paths du template admin
    path('login', views.login, name='login'),
    path('category', views.add_category, name='add_category'),
    path('themes', views.themes, name='themes'),
    path('edit_profile', views.edit_profile, name='edit_profile'),
    path('edit_user', views.edit_user, name='edit_user'),
    path('add_medicine', views.add_medicine, name='add_medicine'),
    path('medicine_grid', views.medicine_grid, name='medicine_grid'),
    #path('medicine_list', views.medicine_list, name='medicine_list'),
    path('my_profile', views.my_profile, name='my_profile'),
    path('notification_expired', views.notification_date_expired, name='notification_date_expired'),
    path('notification_out_stock', views.notification_out_of_stock, name='notification_out_of_stock'),
    path('email', views.send_email, name='send_email'),
    path('user_activity', views.user_activity, name='user_medicine'),
    path('user_list', views.user_list, name='user_list'),

    #path de création de catégorie
    path('category_creation', views.creation_categorie, name='creation_categorie'),
    path('category_medicament', views.creation_medicament, name='creation_medicament'),
    path('page_connexion', views.page_connexion, name='page_connexion'),
    path('category_affichage', views.liste_category, name='liste_category'),
    path('supprimer_categorie/<int:categorie_id>/', views.supprimer_categorie, name='supprimer_categorie'),
    path('supprimer_medicament/<int:medicament_id>/', views.supprimer_medicament, name='supprimer_medicament'),
    path('modifier_medicament/<int:medicament_id>/', views.modifier_medicament, name='vmodifier_medicament'),
    path('liste_medicaments', views.liste_medicaments, name='liste_medicaments'),
    path('show_details/<int:id>/', views.show_details, name='show_details'),


    path('', views.liste_medicaments_client, name='liste_medicaments_client'),

]   + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

