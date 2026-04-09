from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivymd.uix.list import OneLineListItem, ThreeLineAvatarIconListItem, IconLeftWidget, IconRightWidget
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.label import MDLabel
from kivy.metrics import dp
from kivymd.uix.card import MDCard
from kivy.animation import Animation
from datetime import datetime
import sys
import os

# --- CORRECTION DES CHEMINS ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from utilisateur.profil import profil
from utilisateur.profil.modification import modifier_profil 
import Database

Window.size = (400, 800)

class ServiceCard(MDCard):
    """Classe pour les cartes d'aperçu des services avec animation"""
    image_source = StringProperty("")
    title_text = StringProperty("")
    expanded = BooleanProperty(False)

    def toggle_expansion(self):
        self.expanded = not self.expanded
        target_height = self.ids.sub_services_list.minimum_height if self.expanded else 0
        target_opacity = 1 if self.expanded else 0
        anim = Animation(height=target_height, opacity=target_opacity, duration=0.2, t='out_quad')
        anim.start(self.ids.sub_services_list)

class ConciergerieApp(MDApp):
    utilisateur_courant = None 
    current_service_id = NumericProperty(0)

    def build(self):
        self.theme_cls.primary_palette = "Red"
        
        sm = Builder.load_file("login.kv")
        
        chemin_insc = os.path.join(ROOT_DIR, 'inscription', 'inscription.kv')
        sm.add_widget(Builder.load_file(chemin_insc))

        chemin_accueil = os.path.join(ROOT_DIR, 'utilisateur', 'Accueil', 'Accueil.kv')
        self.ecran_client = Builder.load_file(chemin_accueil)
        sm.add_widget(self.ecran_client)

        chemin_modif = os.path.join(ROOT_DIR, 'utilisateur', 'profil', 'modification', 'modifier_profil.kv')
        self.ecran_modif = Builder.load_file(chemin_modif)
        sm.add_widget(self.ecran_modif)

        chemin_contact = os.path.join(ROOT_DIR, 'contact.kv')
        self.ecran_contact = Builder.load_file(chemin_contact)
        sm.add_widget(self.ecran_contact)
        
        return sm

    # ==========================================
    # NAVIGATION PRINCIPALE
    # ==========================================
    def aller_a_inscription(self):
        self.root.current = "page_inscription"

    def aller_a_connexion(self):
        self.root.current = "page_connexion"

    def deconnexion(self):
        self.utilisateur_courant = None
        self.root.current = "page_connexion"
        self.root.ids.champ_email.text = ""
        self.root.ids.champ_mdp.text = ""

    def retour_profil(self):
        self.root.current = "espace_client"

    def aller_vers_modifier_profil(self):
        if self.utilisateur_courant:
            self.root.current = "page_modifier_profil"
            modifier_profil.charger_donnees(self.ecran_modif, self.utilisateur_courant)

    def aller_vers_contact(self):
        self.root.current = "page_contact"

    # ==========================================
    # LOGIQUE RECHERCHE ET PANIER (Fusionnée)
    # ==========================================
    def filter_services(self, query=""):
        try:
            recherche_ui = self.ecran_client.ids.contenu_recherche.ids
            container = recherche_ui.container_prestations
            container.clear_widgets()
            query = query.lower().strip()
            
            all_categories = Database.get_categories()

            for category in all_categories:
                cat_name_display = category["nom"].strip()
                cat_name_lower = cat_name_display.lower()
                all_types = Database.get_type_prestas_by_category(category['id_categorie'])
                matching_types = [t for t in all_types if query in t["nom"].lower()]
                
                if query == "" or query in cat_name_lower or matching_types:
                    img_path = os.path.join(ROOT_DIR, 'images', f"{cat_name_lower}.jpg")
                    card = ServiceCard(image_source=img_path, title_text=cat_name_display)
                    list_to_show = all_types if (query == "" or query in cat_name_lower) else matching_types
                    
                    for p in list_to_show:
                        item = OneLineListItem(text=f"{p['nom']} - {p['prix']}€", divider="Full", on_release=lambda x, data=p: self.ouvrir_details(data))
                        card.ids.sub_services_list.add_widget(item)
                    container.add_widget(card)
        except Exception as e:
            print(f"Attente d'initialisation : {e}")

    def ouvrir_details(self, data):
        recherche_ui = self.ecran_client.ids.contenu_recherche.ids
        self.current_service_id = data['id_type_presta']
        recherche_ui.detail_titre.text = data['nom']
        recherche_ui.detail_desc.text = data['description']
        recherche_ui.detail_prix.text = f"Prix : {data['prix']} €"
        recherche_ui.input_date.text = datetime.now().strftime("%d/%m/%Y")
        recherche_ui.input_hour.text = ""
        recherche_ui.search_screen_manager.transition.direction = "left"
        recherche_ui.search_screen_manager.current = 'details_presta'

    def ouvrir_panier(self):
        self.charger_panier()
        recherche_ui = self.ecran_client.ids.contenu_recherche.ids
        recherche_ui.search_screen_manager.transition.direction = "left"
        recherche_ui.search_screen_manager.current = 'page_panier'

    def charger_panier(self):
        recherche_ui = self.ecran_client.ids.contenu_recherche.ids
        panier_list = recherche_ui.panier_list
        panier_list.clear_widgets()
        
        user_id = self.utilisateur_courant['id_user'] if self.utilisateur_courant else 1
        items = Database.get_user_panier(user_id)
        total = 0
        
        for item in items:
            total += float(item['prix'])
            dt = item.get('debut_contrat', '')
            date_formatee = dt.strftime("%d/%m/%Y à %Hh%M") if isinstance(dt, datetime) else str(dt)
            row = ThreeLineAvatarIconListItem(text=item['nom'], secondary_text=f"Prix : {item['prix']}€", tertiary_text=f"{date_formatee}")
            row.add_widget(IconLeftWidget(icon="tag-outline"))
            delete_btn = IconRightWidget(icon="trash-can-outline", theme_text_color="Error", on_release=lambda x, id_p=item['id_presta']: self.supprimer_du_panier(id_p))
            row.add_widget(delete_btn)
            panier_list.add_widget(row)
            
        recherche_ui.total_label.text = f"{total:.2f} €"

    def supprimer_du_panier(self, id_presta):
        try:
            Database.delete_prestation(id_presta)
            self.charger_panier()
            self.afficher_message("Prestation supprimée", couleur=[1, 0, 0, 1])
        except Exception as e: 
            self.afficher_message(f"Erreur : {e}")

    def ajouter_prestation(self):
        recherche_ui = self.ecran_client.ids.contenu_recherche.ids
        date_txt = recherche_ui.input_date.text.strip()
        heure_txt = recherche_ui.input_hour.text.strip()
        
        if not date_txt or not heure_txt:
            self.afficher_message("Remplissez la date et l'heure !", couleur=[1, 0, 0, 1])
            return
        try:
            h = int(heure_txt)
            if not (8 <= h <= 16):
                self.afficher_message("L'heure doit être entre 8 et 16", couleur=[1, 0, 0, 1])
                return
            date_obj = datetime.strptime(date_txt, "%d/%m/%Y")
            dt_mysql = date_obj.replace(hour=h, minute=0, second=0).strftime('%Y-%m-%d %H:%M:%S')
            
            user_id = self.utilisateur_courant['id_user'] if self.utilisateur_courant else 1
            Database.create_prestation(id_user=user_id, id_type_presta=self.current_service_id, debut=dt_mysql, fin=None, adresse="À définir")
            
            self.afficher_message("Ajouté au panier !")
            recherche_ui.search_screen_manager.transition.direction = "right"
            recherche_ui.search_screen_manager.current = 'liste_recherche'
        except ValueError: 
            self.afficher_message("Format Date ou Heure invalide !", couleur=[1, 0, 0, 1])
        except Exception as e: 
            self.afficher_message(f"Erreur : {str(e)}")

    def payer_commande(self):
        try:
            user_id = self.utilisateur_courant['id_user'] if self.utilisateur_courant else 1
            Database.valider_panier_db(user_id)
            self.charger_panier()
            self.afficher_message("Réservation en attente de validation", couleur=[0, 0.6, 0, 1])
            
            recherche_ui = self.ecran_client.ids.contenu_recherche.ids
            recherche_ui.search_screen_manager.transition.direction = "right"
            recherche_ui.search_screen_manager.current = 'liste_recherche'
        except Exception as e: 
            self.afficher_message(f"Erreur lors du paiement : {e}")

    def afficher_message(self, texte, couleur=[0.4, 0.1, 0.2, 1]):
        try:
            snackbar = Snackbar(bg_color=couleur)
            label = MDLabel(text=texte, theme_text_color="Custom", text_color=[1, 1, 1, 1], valign="center")
            snackbar.add_widget(label)
            snackbar.open()
        except: 
            print(f"Notification : {texte}")

    # ==========================================
    # LOGIQUE PROFIL & CONTACT
    # ==========================================
    def sauvegarder_profil(self):
        nom = self.ecran_modif.ids.modif_nom.text
        prenom = self.ecran_modif.ids.modif_prenom.text
        email = self.ecran_modif.ids.modif_email.text
        tel = self.ecran_modif.ids.modif_tel.text
        adr = self.ecran_modif.ids.modif_adresse.text

        Database.update_user_details(self.utilisateur_courant['id_user'], nom, prenom, email, tel, adr)
        self.utilisateur_courant = Database.get_users_details(self.utilisateur_courant['id_user'])
        widget_p = self.ecran_client.ids.contenu_profil
        profil.charger_donnees_profil(widget_p, self.utilisateur_courant)
        self.retour_profil()

    def envoyer_contact(self, nom, prenom, adresse, ville, email, telephone, message):
        if not nom or not prenom or not email or not message:
            print("Erreur : Les champs obligatoires ne sont pas remplis.")
            return
        print(f"Demande reçue de {nom} {prenom} ({email}) : {message}")
        self.ecran_contact.ids.contact_message.text = ""
        self.retour_profil()

    # ==========================================
    # CONNEXION / INSCRIPTION
    # ==========================================
    def tenter_connexion(self, email_saisi, mdp_saisi):
        self.root.ids.message_erreur.text = ""
        if not email_saisi or not mdp_saisi:
            self.root.ids.message_erreur.text = "Veuillez remplir tous les champs."
            return

        try:
            utilisateur = Database.authenticate_users(email_saisi, mdp_saisi)
            if not utilisateur:
                self.root.ids.message_erreur.text = "Email ou mot de passe incorrect."
                return

            role = Database.get_user_role(utilisateur['id_user'])
            if role == "client":
                self.utilisateur_courant = utilisateur
                self.root.current = "espace_client"
                
                widget_p = self.ecran_client.ids.contenu_profil
                profil.charger_donnees_profil(widget_p, utilisateur)
                self.filter_services("") 
            else:
                self.root.current = f"espace_{role}"
        except Exception as e:
            print(f"Erreur BDD : {e}")
            self.root.ids.message_erreur.text = "Erreur de connexion au serveur."

    def tenter_inscription(self, nom, prenom, email, mdp):
        ecran_insc = self.root.get_screen("page_inscription")
        label_msg = ecran_insc.ids.message_erreur_insc
        if not nom or not prenom or not email or not mdp:
            label_msg.text = "Veuillez remplir tous les champs."
            return

        try:
            if Database.user_exists(email):
                label_msg.text = "Cet email est déjà utilisé."
                return

            if Database.create_users(nom, prenom, email, mdp):
                label_msg.theme_text_color = "Custom"
                label_msg.text_color = (0, 0.6, 0, 1)
                label_msg.text = "Compte créé ! Redirection..."
                Clock.schedule_once(lambda dt: self.aller_a_connexion(), 1.5)
        except Exception as e:
            label_msg.text = "Erreur lors de l'inscription."

if __name__ == "__main__":
    ConciergerieApp().run()