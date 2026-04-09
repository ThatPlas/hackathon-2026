from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
import sys
import os

# Permet à Python de remonter d'un dossier pour trouver "Database.py"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import Database

Window.size = (400, 800)

class InscriptionApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Red"
        return Builder.load_file("inscription.kv")

    def tenter_inscription(self, nom, prenom, email, mdp):
        """Fonction déclenchée par le bouton S'inscrire"""
        label_msg = self.root.ids.message_erreur_insc
        label_msg.theme_text_color = "Error" # Rouge par défaut
        label_msg.text = ""

        # 1. Vérification des champs
        if not nom or not prenom or not email or not mdp:
            label_msg.text = "Veuillez remplir tous les champs."
            return

        try:
            # 2. Vérification si l'email existe déjà dans la BDD
            if Database.user_exists(email):
                label_msg.text = "Cet email est déjà utilisé."
                return

            # 3. Création de l'utilisateur
            succes = Database.create_users(nom, prenom, email, mdp)

            if succes:
                # Si ça a marché, on affiche le message en vert
                label_msg.theme_text_color = "Custom"
                label_msg.text_color = (0, 0.6, 0, 1) # Couleur Verte
                label_msg.text = "Compte créé avec succès !"
            else:
                label_msg.text = "Erreur lors de la création du compte."

        except Exception as e:
            print(f"Erreur BDD : {e}")
            label_msg.text = "Erreur de connexion au serveur."

    def aller_a_connexion(self):
        """Action du bouton retour"""
        # Plus tard, c'est ici que l'on connectera les pages ensemble !
        print("L'utilisateur veut retourner sur la page de Login...")

if __name__ == "__main__":
    InscriptionApp().run()