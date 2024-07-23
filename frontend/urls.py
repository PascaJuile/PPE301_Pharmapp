from . import views
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Paths pour le template client
    path('about', views.about, name='about'),
    path('cart', views.cart, name='cart'),
    path('checkout', views.checkout, name='checkout'),
    path('shop_single', views.shop_single, name='shop_single'),
    path('contact', views.contact, name='contact'),
    path('shop', views.shop, name='shop'),
    path('thankyou', views.thankyou, name='thankyou'),
    path('', views.liste_medicaments_client, name='liste_medicaments_client'),
    path('shop_single/<int:medicament_id>/', views.shop_single, name='shop_single'),
    path('rechercher_medicament', views.rechercher_medicament, name='rechercher_medicament'),
    path('upload_ordonnance', views.upload_ordonnance, name='upload_ordonnance'),
    path('formulaire_achat/<int:ordonnance_id>/', views.formulaire_achat, name='formulaire_achat'),

    # Paths pour le template admin
    path('themes', views.themes, name='themes'),
    path('edit_profile', views.edit_profile, name='edit_profile'),
    path('edit_user', views.edit_user, name='edit_user'),
    path('preparateur/medicine_grid', views.medicine_grid, name='medicine_grid'),
    path('notification_expired', views.notification_date_expired, name='notification_date_expired'),
    path('notification_out_stock', views.notification_out_of_stock, name='notification_out_of_stock'),
    path('email', views.send_email, name='send_email'),
    path('user_activity', views.user_activity, name='user_medicine'),
    path('user_list', views.user_list, name='user_list'),
    path('preparateur/category_creation', views.creation_categorie, name='creation_categorie'),
    path('preparateur/medicament_creation', views.creation_medicament, name='creation_medicament'),
    path('page_connexion', views.page_connexion, name='page_connexion'),
    path('inscription', views.inscription, name='inscription'),
    path('preparateur/category_affichage', views.liste_category, name='liste_category'),
    path('preparateur/supprimer_categorie/<int:categorie_id>/', views.supprimer_categorie, name='supprimer_categorie'),
    path('preparateur/supprimer_medicament/<int:medicament_id>/', views.supprimer_medicament, name='supprimer_medicament'),
    path('preparateur/modifier_medicament/<int:medicament_id>/', views.modifier_medicament, name='vmodifier_medicament'),
    path('preparateur/modifier_categorie/<int:categorie_id>/', views.modifier_categorie, name='vmodifier_categorie'),
    path('preparateur/liste_medicaments', views.liste_medicaments, name='liste_medicaments'),
    path('preparateur/show_details/<int:id>/', views.show_details, name='show_details'),

    # Paths pour le pharmacien
    path('pharmacien/listeMedicaments', views.pharamacien_listeMedicament, name='pharamacien_listeMedicament'),
    path('pharmacien/list_affichage_medicaments', views.pharmacien_affichage_med, name='pharmacien_affichage_med'),
    path('pharmacien/grid_affichage_medicaments', views.pharmacien_affichage_med_grid, name='pharmacien_affichage_med_grid'),
    path('pharmacien/show_details/<int:id>/', views.pharmacien_show_details, name='pharmacien_show_details'),

    # Paths pour le caissier
    path('caissier/medicaments_selectionnés', views.medicaments_selectionnés, name='medicaments_selectionnés'),

    # Path profil utilisateur
    path('profil_utilisateur', views.profil_utilisateur, name='profil_utilisateur'),
]

# Configuration pour servir les fichiers statiques et médias en développement
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
