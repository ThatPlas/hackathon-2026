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

# Importation des modules de logique
from utilisateur.profil import profil
from utilisateur.profil.modification import modifier_profil 
import Database

# Taille d'écran mobile pour le développement
Window.size = (400, 800)

class ServiceCard(MDCard):
    """Classe pour les cartes d'aperçu des services"""
    image_source = StringProperty("")
    title_text = StringProperty("")
    date_text = StringProperty("")

class ConciergerieApp(MDApp):
    utilisateur_courant = None # Stocke les infos de l'utilisateur connecté

    def build(self):
        self.theme_cls.primary_palette = "Red"
        
        # 1. Charger le gestionnaire d'écrans principal
        sm = Builder.load_file("login.kv")
        
        # 2. Charger et ajouter l'écran d'Inscription
        chemin_insc = os.path.join(ROOT_DIR, 'inscription', 'inscription.kv')
        sm.add_widget(Builder.load_file(chemin_insc))

        # 3. Charger et ajouter l'Accueil Client
        chemin_accueil = os.path.join(ROOT_DIR, 'utilisateur', 'Accueil', 'Accueil.kv')
        self.ecran_client = Builder.load_file(chemin_accueil)
        sm.add_widget(self.ecran_client)

        # 4. Charger la page de Modification de Profil
        chemin_modif = os.path.join(ROOT_DIR, 'utilisateur', 'profil', 'modification', 'modifier_profil.kv')
        self.ecran_modif = Builder.load_file(chemin_modif)
        sm.add_widget(self.ecran_modif)

        # 5. Charger la page de Contact (Correction du chemin vers la racine)
        chemin_contact = os.path.join(ROOT_DIR, 'contact.kv')
        self.ecran_contact = Builder.load_file(chemin_contact)
        sm.add_widget(self.ecran_contact)
        
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
        """Ouvre la page de modification avec les infos pré-remplies"""
        if self.utilisateur_courant:
            self.root.current = "page_modifier_profil"
            modifier_profil.charger_donnees(self.ecran_modif, self.utilisateur_courant)

    def aller_vers_contact(self):
        """Ouvre la page de contact"""
        self.root.current = "page_contact"

    # ==========================================
    # LOGIQUE PROFIL & CONTACT
    # ==========================================
    def sauvegarder_profil(self):
        """Enregistre les modifications du profil en BDD"""
        nom = self.ecran_modif.ids.modif_nom.text
        prenom = self.ecran_modif.ids.modif_prenom.text
        email = self.ecran_modif.ids.modif_email.text
        tel = self.ecran_modif.ids.modif_tel.text
        adr = self.ecran_modif.ids.modif_adresse.text

        # Mise à jour SQL
        Database.update_user_details(self.utilisateur_courant['id_user'], nom, prenom, email, tel, adr)

        # Rafraîchissement des données locales
        self.utilisateur_courant = Database.get_users_details(self.utilisateur_courant['id_user'])
        widget_p = self.ecran_client.ids.contenu_profil
        profil.charger_donnees_profil(widget_p, self.utilisateur_courant)

        self.retour_profil()

    def envoyer_contact(self, nom, prenom, adresse, ville, email, telephone, message):
        """Gère l'envoi du formulaire de contact avec tous les champs de votre collègue"""
        if not nom or not prenom or not email or not message:
            print("Erreur : Les champs obligatoires ne sont pas remplis.")
            return
        
        # Simulation d'envoi
        print(f"Demande reçue de {nom} {prenom} de {ville} ({email}) : {message}")
        
        # Réinitialisation du champ message et retour au profil
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

    # ==========================================
    # RECHERCHE SERVICES
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