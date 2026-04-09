from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem
from kivymd.uix.pickers import MDDatePicker
from datetime import datetime
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import Database

class MyApp(MDApp):
    def build(self):
        self.start_date = None
        self.end_date = None
        return Builder.load_file("interface_design.kv")

    def show_date_picker(self):
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

    def remplir_recherche(self, data):
        """
        data: liste de dictionnaires avec des infos à afficher
        Exemple: [{"titre": "Installation", "date": "2026-04-07"}, ...]
        """
        container = self.root.ids.container_recherche
        container.clear_widgets()
        for item in data:
            widget = OneLineListItem(text=f"{item['titre']} - {item['date']}")
            container.add_widget(widget)

    def on_start(self):
    
        test_data = [
            {"titre": "Installation", "date": "2026-04-07"},
            {"titre": "Réparation", "date": "2026-04-08"},
            {"titre": "Maintenance", "date": "2026-04-09"},
        ]
        self.remplir_recherche(test_data)

    def tenter_connexion(self, email, mdp):
        """Fonction déclenchée par le bouton connexion"""
        label_msg = self.root.ids.login_msg
        label_msg.text = ""

        if not email or not mdp:
            label_msg.text = "Veuillez remplir tous les champs."
            return

        if email == "remi" and mdp == "1234":
            
            self.root.ids.profil_nom.text = "Remi Kalkan"
            self.root.ids.profil_email.text = email
            
            if hasattr(self.root, "current"):
                self.root.current = "main_screen"
            else:
        
                for child in self.root.children:
                    if hasattr(child, "current"):
                        child.current = "main_screen"
                        break

        else:
            label_msg.text = "Email ou mot de passe incorrect."

    def valider_dates(self):
        if self.start_date and self.end_date:
            self.filter_prestations_range(self.start_date, self.end_date)
            print(f"Start date : {self.start_date} | End date : {self.end_date}")
        else:
            print("Aucune date sélectionnée !")