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

        chemin_admin = os.path.join(ROOT_DIR, 'admin.kv')
        self.ecran_admin = Builder.load_file(chemin_admin)
        sm.add_widget(self.ecran_admin)

        # === INTEGRATION TECHNICIEN ===
        # === INTEGRATION TECHNICIEN ===
        try:
            from kivymd.uix.screen import MDScreen # On importe l'écran
            chemin_tech = os.path.join(ROOT_DIR, 'tech', 'interface_design.kv')
            
            # self.ecran_tech est la "boîte" de ton collègue
            self.ecran_tech = Builder.load_file(chemin_tech)
            
            # On fabrique un vrai écran "conteneur" pour faire plaisir à Kivy
            ecran_conteneur = MDScreen(name="espace_technicien")
            ecran_conteneur.add_widget(self.ecran_tech)
            
            # On ajoute le conteneur, et cette fois ça passe !
            sm.add_widget(ecran_conteneur)
            print("SUCCÈS : Écran technicien chargé et ajouté !")
        except Exception as e:
            print(f"ERREUR au chargement du technicien : {e}")
        
        # Injecter l'écran de notification
        try:
            recherche_sm = self.ecran_client.ids.contenu_recherche.ids.search_screen_manager
            recherche_sm.add_widget(NotifScreen(name='page_notif'))
        except Exception as e:
            print(f"Erreur injection NotifScreen : {e}")

        return sm

    # ==========================================
    # CONNEXION / REDIRECTION
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