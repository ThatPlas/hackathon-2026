from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivymd.uix.card import MDCard
from kivymd.uix.list import ThreeLineAvatarIconListItem, IconLeftWidget
import sys
import os

# Permet de trouver Database.py dans le dossier parent
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import Database

Window.size = (400, 800)

# --- CLASSE POUR LE DESIGN DE L'ACCUEIL ---
class ServiceCard(MDCard):
    image_source = StringProperty("")
    title_text = StringProperty("")
    date_text = StringProperty("")

class ConciergerieApp(MDApp):
    # Les données de vos prestations
    all_services = [
        {"title": "Maintenance", "img": "../images/maintenance.jpg", "date": "Mis à jour aujourd'hui"},
        {"title": "Rénovation", "img": "../images/renovation.jpg", "date": "Mis à jour hier"},
        {"title": "Entretien", "img": "../images/entretien.jpg", "date": "Mis à jour il y a 2 jours"},
        {"title": "Espaces verts", "img": "../images/espacesverts.jpg", "date": "Mis à jour aujourd'hui"},
    ]

    def build(self):
        self.theme_cls.primary_palette = "Red"
        
        # 1. Charger la Connexion (Le Chef de gare : ScreenManager)
        sm = Builder.load_file("login.kv")
        
        # 2. Charger et attacher l'Inscription (C'est ce que j'avais oublié !)
        chemin_insc = os.path.join(os.path.dirname(__file__), '..', 'inscription', 'inscription.kv')
        ecran_insc = Builder.load_file(chemin_insc)
        sm.add_widget(ecran_insc)

        # 3. Charger et attacher l'Accueil Client
        chemin_accueil = os.path.join(os.path.dirname(__file__), '..', 'utilisateur', 'Accueil', 'Accueil.kv')
        self.ecran_client = Builder.load_file(chemin_accueil)
        sm.add_widget(self.ecran_client)
        
        return sm

    # ==========================================
    # NAVIGATION ENTRE CONNEXION ET INSCRIPTION
    # ==========================================
    def aller_a_inscription(self):
        """Déclenché par le bouton sur la page de connexion"""
        self.root.current = "page_inscription"

    def aller_a_connexion(self):
        """Déclenché par le bouton sur la page d'inscription"""
        self.root.current = "page_connexion"

    # ==========================================
    # LOGIQUE DE CONNEXION
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

            id_trouve = utilisateur['id_user']
            role = Database.get_user_role(id_trouve)

            if role == "client":
                # On bascule sur l'accueil client et on initialise les données !
                self.root.current = "espace_client"
                self.initialiser_accueil_client()
            elif role == "admin":
                self.root.current = "espace_admin"
            elif role == "technicien":
                self.root.current = "espace_technicien"
            else:
                self.root.ids.message_erreur.text = "Erreur : Profil sans rôle défini."

        except Exception as e:
            print(f"Erreur de base de données : {e}")
            self.root.ids.message_erreur.text = "Erreur de connexion au serveur."

    # ==========================================
    # LOGIQUE D'INSCRIPTION
    # ==========================================
    def tenter_inscription(self, nom, prenom, email, mdp):
        ecran_insc = self.root.get_screen("page_inscription")
        label_msg = ecran_insc.ids.message_erreur_insc
        label_msg.theme_text_color = "Error"
        label_msg.text = ""

        if not nom or not prenom or not email or not mdp:
            label_msg.text = "Veuillez remplir tous les champs."
            return

        try:
            if Database.user_exists(email):
                label_msg.text = "Cet email est déjà utilisé."
                return

            succes = Database.create_users(nom, prenom, email, mdp)

            if succes:
                label_msg.theme_text_color = "Custom"
                label_msg.text_color = (0, 0.6, 0, 1) # Vert
                label_msg.text = "Compte créé avec succès !"
                # Bascule vers connexion après 1.5s
                Clock.schedule_once(lambda dt: self.aller_a_connexion(), 1.5)
            else:
                label_msg.text = "Erreur lors de la création du compte."

        except Exception as e:
            print(f"Erreur de base de données : {e}")
            label_msg.text = "Erreur de connexion au serveur."

    # ==========================================
    # LOGIQUE DE L'ACCUEIL CLIENT
    # ==========================================
    def initialiser_accueil_client(self):
        """Remplit la liste et les cartes au démarrage"""
        self.filter_services("") # Affiche toutes les cartes
        
        try:
            list_view = self.ecran_client.ids.prestations_list
            list_view.clear_widgets()
            for i in range(3):
                item = ThreeLineAvatarIconListItem(
                    text=f"Prestation {i+1}",
                    secondary_text="Historique d'intervention",
                    tertiary_text="Terminé"
                )
                item.add_widget(IconLeftWidget(icon="clock-outline"))
                list_view.add_widget(item)
        except Exception as e:
            pass

    def filter_services(self, query=""):
        """Gère la recherche de prestations"""
        container = self.ecran_client.ids.container_prestations
        container.clear_widgets()

        for service in self.all_services:
            if query.lower() in service["title"].lower():
                card = ServiceCard(
                    image_source=service["img"],
                    title_text=service["title"],
                    date_text=service["date"]
                )
                container.add_widget(card)

if __name__ == "__main__":
    ConciergerieApp().run()