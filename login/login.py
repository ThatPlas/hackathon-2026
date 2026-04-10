from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivymd.uix.list import OneLineListItem, ThreeLineAvatarIconListItem, IconLeftWidget, IconRightWidget, TwoLineAvatarIconListItem, ImageLeftWidget
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.label import MDLabel
from kivy.metrics import dp
from kivymd.uix.card import MDCard
from kivy.animation import Animation
from datetime import datetime
from kivymd.uix.screen import MDScreen
import sys
import os

# --- CORRECTION DES CHEMINS ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from notif.notif import NotifScreen 
from utilisateur.profil import profil
from utilisateur.profil.modification import modifier_profil 
import Database

class ServiceCard(MDCard):
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
    presta_actuelle_id = NumericProperty(None)

    def build(self):
        self.theme_cls.primary_palette = "Red"
        
        # 1. Charger le KV des notifications
        try:
            chemin_notif_kv = os.path.join(ROOT_DIR, 'notif', 'notif.kv')
            Builder.load_file(chemin_notif_kv)
        except Exception as e:
            print(f"Note : notif.kv non chargé : {e}")

        # 2. Charger le ScreenManager principal
        sm = Builder.load_file("login.kv")
        
        # Ajout des différents écrans
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

        # --- AJOUT DE L'ÉCRAN ADMIN (CORRIGÉ) ---
        try:
            chemin_admin = os.path.join(ROOT_DIR, 'admin', 'admin.kv')
            # On charge le contenu du fichier KV
            contenu_admin = Builder.load_file(chemin_admin)
            
            # On crée un véritable Screen pour accueillir ce contenu
            self.ecran_admin = MDScreen(name="espace_admin")
            self.ecran_admin.add_widget(contenu_admin)
            
            # On ajoute le Screen au manager principal
            sm.add_widget(self.ecran_admin)
        except Exception as e:
            print(f"Erreur chargement Admin : {e}")
        # 3. Injecter l'écran de notification dans le ScreenManager de la Recherche
        try:
            recherche_sm = self.ecran_client.ids.contenu_recherche.ids.search_screen_manager
            recherche_sm.add_widget(NotifScreen(name='page_notif'))
        except Exception as e:
            print(f"Erreur injection NotifScreen : {e}")

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
    # LOGIQUE RECHERCHE, PANIER ET NOTIF
    # ==========================================
    # Dans login.py (ou recherche.py selon ton fichier de lancement)

    def ouvrir_notif(self):
        """Ouvre l'écran des notifications depuis n'importe quel onglet"""
        try:
            # 1. On bascule vers l'onglet recherche (nommé 'page_recherche' dans ton Accueil.kv)
            self.ecran_client.ids.nav_bar.switch_tab('page_recherche') 
            
            # 2. On accède au manager de recherche pour afficher les notifs
            recherche_ui = self.ecran_client.ids.contenu_recherche.ids
            recherche_ui.search_screen_manager.transition.direction = "left"
            recherche_ui.search_screen_manager.current = 'page_notif'
            
        except Exception as e:
            print(f"Erreur navigation notif : {e}")

    def retour_recherche(self):
        """Retourne à la liste des prestations depuis les notifs"""
        recherche_ui = self.ecran_client.ids.contenu_recherche.ids
        recherche_ui.search_screen_manager.transition.direction = "right"
        recherche_ui.search_screen_manager.current = 'liste_recherche'

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
            self.utilisateur_courant = utilisateur

            if role == "client":
                self.root.current = "espace_client"
                profil.charger_donnees_profil(self.ecran_client.ids.contenu_profil, utilisateur)
                self.filter_services("") 
            
            elif role == "admin":
                self.root.current = "espace_admin"
                self.charger_apercu_rapide()
            
            # === REDIRECTION TECHNICIEN ===
            # === REDIRECTION TECHNICIEN ===
            elif role == "technicien":
                self.root.current = "espace_technicien"
                
                # --- NOUVEAU : On saute l'écran de connexion du technicien ---
                self.ecran_tech.ids.screen_manager.current = "main_screen"
                
                # Le reste ne change pas
                self.ecran_tech.ids.profil_nom.text = f"{utilisateur['prenom']} {utilisateur['nom']}"
                self.ecran_tech.ids.profil_email.text = utilisateur['email']
                self.charger_donnees_technicien()
            
            else:
                self.root.current = "page_connexion"
        except Exception as e:
            print(f"Erreur connexion : {e}")
            self.root.ids.message_erreur.text = "Erreur serveur."

    # ==========================================
    # LOGIQUE TECHNICIEN (Adaptée de tech/App.py)
    # ==========================================
    def charger_donnees_technicien(self):
        """Initialise les listes de l'interface technicien"""
        for container_id, p_type in [("container_prestations", "historique"), 
                                    ("container_en_cours", "en_cours"), 
                                    ("upcoming_container", "a_venir")]:
            container = self.ecran_tech.ids[container_id]
            container.clear_widgets()
            # Ici on peut utiliser des données simulées ou appeler Database.get_tech_latest_prestas
            for item in self.get_mock_data_tech(p_type):
                container.add_widget(self.create_prestation_item_tech(item))

    def get_mock_data_tech(self, p_type):
        """Données de test pour le technicien"""
        data = {
            "historique": [{"titre": "Audit sécurité", "info": "10/03/2026", "type": "historique"}],
            "en_cours": [{"titre": "Entretien espaces verts", "info": "Aujourd'hui", "type": "en_cours"}],
            "a_venir": [{"titre": "Audit IT", "info": "20/04/2026", "type": "a_venir"}]
        }
        return data.get(p_type, [])

    def create_prestation_item_tech(self, data):
        """Crée une carte pour la liste du technicien"""
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.button import MDIconButton
        
        card = MDCard(orientation="horizontal", size_hint=(1, None), height=dp(65), radius=[12], elevation=2, padding=dp(8))
        text_layout = MDBoxLayout(orientation="vertical")
        text_layout.add_widget(MDLabel(text=data["titre"], font_style="Body1", bold=True))
        text_layout.add_widget(MDLabel(text=data["info"], font_style="Caption", theme_text_color="Secondary"))
        
        btn = MDIconButton(icon="dots-vertical")
        btn.bind(on_release=lambda x: self.ouvrir_detail_tech(data))
        
        card.add_widget(text_layout)
        card.add_widget(btn)
        return card

    def ouvrir_detail_tech(self, data):
        """Affiche les détails d'une prestation pour le technicien"""
        p_type = data.get("type", "historique")
        ids = self.ecran_tech.ids
        
        # Mapping des préfixes d'ID définis dans interface_design.kv
        prefix = "hi_" if p_type == "historique" else "ec_" if p_type == "en_cours" else "av_"
        target = f"detail_{p_type}"
        
        # Remplissage des champs (simulé)
        ids[f"{prefix}subtitle"].text = data["titre"]
        ids[f"{prefix}adresse"].text = "13 rue du test, Lille"
        
        ids.screen_manager.current = target

    # (Garde tes autres fonctions aller_a_inscription, deconnexion, etc.)
    def deconnexion(self):
        self.utilisateur_courant = None
        self.root.current = "page_connexion"
        self.root.ids.champ_email.text = ""
        self.root.ids.champ_mdp.text = ""

if __name__ == "__main__":
    ConciergerieApp().run()