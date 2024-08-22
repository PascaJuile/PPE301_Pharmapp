
from . import views
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import chart_data


urlpatterns = [
    # Paths pour le template client
    path('about', views.about, name='about'),
    path('cart', views.cart, name='cart'),
    path('checkout', views.checkout, name='checkout'),
    path('shop_single', views.shop_single, name='shop_single'),
    path('contact/', views.contact, name='contact'),
    path('shop', views.shop, name='shop'),
    path('thankyou', views.thankyou, name='thankyou'),
    path('', views.liste_medicaments_client, name='liste_medicaments_client'),
    path('shop_single/<int:medicament_id>/', views.shop_single, name='shop_single'),
    path('rechercher_medicament', views.rechercher_medicament, name='rechercher_medicament'),
    path('formulaire_achat/<int:ordonnance_id>/', views.formulaire_achat, name='commanlaire_achat'),
    path('client/commande', views.commande_client, name='commande_client'),
    path('client/inscription', views.inscription_client, name='inscription_client'),
    path('client/redirection', views.redirection_commande, name='redirection_commande'),
    path('client/payement_commande', views.payement_commande, name='payement_commande'),
    path('client/details_livraison', views.details_livraison_client, name='details_livraison_client'),
    path('client/historique_commandes/', views.historique_commandes_client, name='historique_commandes'),





    # Paths pour le template admin
    path('preparateur/homepage', views.homepage_prepa, name='homepage_prepa'),
    path('client/homepage', views.homepage_cli, name='homepage_cli'),
    path('pharmacien/homepage', views.homepage_phar, name='homepage_phar'),
    path('chart-data/', chart_data, name='chart_data'),
    path('caissier/homepage', views.homepage_car, name='homepage_car'),
    path('livreur/homepage', views.homepage_liv, name='homepage_liv'),
    path('page/admin', views.homepage_ges, name='homepage_ges'),
    path('preparateur/themes', views.themes, name='themes'),
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
    path('deconnexion', views.deconnexion, name='deconnexion'),
    path('preparateur/category_affichage', views.liste_category, name='liste_category'),
    path('preparateur/supprimer_categorie/<int:categorie_id>/', views.supprimer_categorie, name='supprimer_categorie'),
    path('preparateur/supprimer_medicament/<int:medicament_id>/', views.supprimer_medicament, name='supprimer_medicament'),
    path('preparateur/modifier_medicament/<int:medicament_id>/', views.modifier_medicament, name='vmodifier_medicament'),
    path('preparateur/modifier_categorie/<int:categorie_id>/', views.modifier_categorie, name='vmodifier_categorie'),
    path('preparateur/liste_medicaments', views.liste_medicaments, name='liste_medicaments'),
    path('preparateur/show_details/<int:id>/', views.show_details, name='show_details'),

    # Paths pour le pharmacien
    #path('pharmacien/page1', views.pharamacien_listeMedicament, name='page1'),
    path('pharmacien/creer_commande', views.creer_commande, name='creer_commande'),
    path('recherche_medicament/', views.recherche_medicament, name='recherche_medicament'),
    path('pharmacien/listeMedicaments', views.pharamacien_listeMedicament, name='pharamacien_listeMedicament'),
    path('pharmacien/list_affichage_medicaments', views.pharmacien_affichage_med, name='pharmacien_affichage_med'),
    path('pharmacien/grid_affichage_medicaments', views.pharmacien_affichage_med_grid, name='pharmacien_affichage_med_grid'),
    path('pharmacien/show_details/<int:id>/', views.pharmacien_show_details, name='pharmacien_show_details'),
    path('pharmacien/listeCommande', views.journal_medicaments_selectionnes, name='journal_medicaments_selectionnes'),
    path('pharmacien/supprimer_commande/<int:pk>', views.delete_order, name='delete_order'),  
    path('pharmacien/commandeVirtuelle/<int:commande_id>/', views.pharmacien_commandeVirtuelle, name='pharmacien_commandeVirtuelle'),
    path('pharmacien/commandeVirtuelle', views.liste_commandes_virtuelles, name='liste_commandes_virtuelles'),
    path('pharmacien/commandeVirtuelle/<int:commande_id>/accepter/', views.accepter_commande, name='accepter_commandeV'),
    path('pharmacien/commandeVirtuelle/<int:commande_id>/refuser/', views.refuser_commande, name='refuser_commandeV'),
    
    # Paths pour le caissier
    path('caissier/commande_non_validee', views.afficher_medicaments_selectionnes, name='afficher_medicaments_selectionnes'),
    path('caissier/liste_commande', views.caissier_commandes_validees, name='caissier_commandes_validees'),
    path('caissier/assigner_livreur/', views.assigner_livreur, name='assigner_livreur'),

    # Path profil utilisateur
    path('profil_utilisateur', views.profil_utilisateur, name='profil_utilisateur'),

    #Path livreur
    path('livreur/liste_livraison/', views.liste_livraisons_livreur, name='liste_livraisons_livreur'),

    #Path gestionnaire en pharmacie
    path('gestionnaire/inscription', views.inscription, name='inscription'),
    path('gestionnaire/liste_gestionnaire', views.liste_utilisateur_ges, name='liste_ges'),
    path('gestionnaire/liste_preparateur', views.liste_utilisateur_prepa, name='liste_prepa'),
    path('gestionnaire/liste_caissier', views.liste_utilisateur_cas, name='liste_cas'),
    path('gestionnaire/liste_pharmacien', views.liste_utilisateur_phar, name='liste_phar'),
    path('gestionnaire/liste_livreur', views.liste_utilisateur_liv, name='liste_liv'),
    path('gestionnaire/liste_client', views.liste_utilisateur_client, name='liste_client'),
    path('gestionnaire/statistique', views.rapport, name='rapport'),



]

# Configuration pour servir les fichiers statiques et médias en développement
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
