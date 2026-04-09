from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.fitimage import FitImage
from kivymd.uix.list import ThreeLineAvatarIconListItem, IconLeftWidget, IconRightWidget
from kivy.metrics import dp
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.textfield.textfield import MDTextField
from kivymd.uix.card import MDCard
from kivy.properties import StringProperty
from kivymd.uix.fitimage import FitImage
from datetime import datetime
from Historique import Historique
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.list import OneLineListItem
from kivy.core.window import Window
import sys
import os

# Permet à Python de remonter d'un dossier pour trouver "Database.py"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import Database
class MyApp(MDApp):

    def build(self):
        self.start_date = None
        self.end_date = None
        return Builder.load_file("interface_design.kv")

    def show_date_picker(self):
        from kivymd.uix.pickers import MDDatePicker
        date_dialog = MDDatePicker(mode="range")
        date_dialog.bind(on_save=self.on_save_date)
        date_dialog.open()

    def on_save_date(self, instance, value, date_range):
        if date_range:
            self.start_date = date_range[0].strftime("%Y-%m-%d")
            self.end_date = date_range[-1].strftime("%Y-%m-%d")
            self.root.ids.field.text = f"{self.start_date} → {self.end_date}"
            self.filter_prestations_range(self.start_date, self.end_date)

    def filter_prestations_range(self, start_str, end_str):
        container = self.root.ids.container_prestations
        container.clear_widgets()

        prestations = [
            {"date": "2026-04-07", "nom": "Installation"},
            {"date": "2026-04-08", "nom": "Réparation"},
            {"date": "2026-04-09", "nom": "Maintenance"},
            {"date": "2026-04-10", "nom": "Audit"},
        ]

        start = datetime.strptime(start_str, "%Y-%m-%d")
        end = datetime.strptime(end_str, "%Y-%m-%d")

        for p in prestations:
            d = datetime.strptime(p["date"], "%Y-%m-%d")
            if start <= d <= end:
                item = OneLineListItem(text=f"{p['nom']} ({p['date']})")
                container.add_widget(item)

    def valider_dates(self):
        if self.start_date and self.end_date:
            self.filter_prestations_range(self.start_date, self.end_date)
            print("Start date : {} | End date : {}".format(self.start_date, self.end_date))
        else:
            print("Aucune date sélectionnée !")

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