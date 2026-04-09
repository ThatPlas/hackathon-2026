from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivymd.uix.card import MDCard
import sys
import os

# --- CORRECTION DES CHEMINS ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# Imports avec le bon dossier "modification"
from utilisateur.profil import profil
from utilisateur.profil.modification import modifier_profil 
import Database

Window.size = (400, 800)

class ServiceCard(MDCard):
    image_source = StringProperty("")
    title_text = StringProperty("")
    date_text = StringProperty("")

class ConciergerieApp(MDApp):
    utilisateur_courant = None

    def build(self):
        self.theme_cls.primary_palette = "Red"
        
        sm = Builder.load_file("login.kv")
        
        # Inscription
        chemin_insc = os.path.join(ROOT_DIR, 'inscription', 'inscription.kv')
        sm.add_widget(Builder.load_file(chemin_insc))

        # Accueil
        chemin_accueil = os.path.join(ROOT_DIR, 'utilisateur', 'Accueil', 'Accueil.kv')
        self.ecran_client = Builder.load_file(chemin_accueil)
        sm.add_widget(self.ecran_client)

        # --- LE CHEMIN CORRIGÉ EST ICI ---
        # Modifier Profil (Nouvelle Page dans le dossier modification)
        chemin_modif = os.path.join(ROOT_DIR, 'utilisateur', 'profil', 'modification', 'modifier_profil.kv')
        self.ecran_modif = Builder.load_file(chemin_modif)
        sm.add_widget(self.ecran_modif)
        
        return sm

    # ==========================================
    # NAVIGATION
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

    def sauvegarder_profil(self):
        # 1. Récupérer
        nom = self.ecran_modif.ids.modif_nom.text
        prenom = self.ecran_modif.ids.modif_prenom.text
        email = self.ecran_modif.ids.modif_email.text
        tel = self.ecran_modif.ids.modif_tel.text
        adr = self.ecran_modif.ids.modif_adresse.text

        # 2. Sauvegarder
        Database.update_user_details(self.utilisateur_courant['id_user'], nom, prenom, email, tel, adr)

        # 3. Rafraîchir
        self.utilisateur_courant = Database.get_users_details(self.utilisateur_courant['id_user'])
        widget_p = self.ecran_client.ids.contenu_profil
        profil.charger_donnees_profil(widget_p, self.utilisateur_courant)

        # 4. Retour
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

            id_trouve = utilisateur['id_user']
            role = Database.get_user_role(id_trouve)

            if role == "client":
                self.utilisateur_courant = utilisateur
                self.root.current = "espace_client"
                
                widget_p = self.ecran_client.ids.contenu_profil
                profil.charger_donnees_profil(widget_p, utilisateur)
                
                self.filter_services("") 
            elif role == "admin":
                self.root.current = "espace_admin"
            elif role == "technicien":
                self.root.current = "espace_technicien"
            else:
                self.root.ids.message_erreur.text = "Erreur : Rôle non défini."

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

    # ==========================================
    # RECHERCHE
    # ==========================================
    def filter_services(self, query=""):
        container = self.ecran_client.ids.container_prestations
        container.clear_widgets()
        
        img_path = os.path.join(ROOT_DIR, 'images')
        services = [
            {"title": "Maintenance", "img": os.path.join(img_path, "maintenance.jpg"), "date": "Aujourd'hui"},
            {"title": "Rénovation", "img": os.path.join(img_path, "renovation.jpg"), "date": "Hier"},
            {"title": "Entretien", "img": os.path.join(img_path, "entretien.jpg"), "date": "Il y a 2 jours"},
        ]

        for s in services:
            if query.lower() in s["title"].lower():
                container.add_widget(ServiceCard(image_source=s["img"], title_text=s["title"], date_text=s["date"]))

if __name__ == "__main__":
    ConciergerieApp().run()