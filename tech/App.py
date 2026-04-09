from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.metrics import dp
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.clock import Clock
from datetime import datetime
import sys
import os

# Permet à Python de trouver Database.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import Database


class MyApp(MDApp):
    def build(self):
        self.start_date = None
        self.end_date = None
        return Builder.load_file("interface_design.kv")

    def on_start(self):
        # Affiche directement l'onglet Recherche
        self.afficher_recherche_template()
        # Lie les TextField du mot de passe pour activer le bouton automatiquement
        self.root.ids.current_password.bind(text=lambda *x: self.check_fields_mdp())
        self.root.ids.new_password.bind(text=lambda *x: self.check_fields_mdp())
        self.root.ids.confirm_password.bind(text=lambda *x: self.check_fields_mdp())

    # ------------------- Connexion -------------------
    def tenter_connexion(self, email, mdp):
        label_msg = self.root.ids.login_msg
        label_msg.text = ""
        if not email or not mdp:
            label_msg.text = "Veuillez remplir tous les champs."
            return

        # Ici tu peux remplacer par ta vérification SQL
        if email == "remi" and mdp == "1234":
            self.root.ids.profil_nom.text = "Remi Kalkan"
            self.root.ids.profil_email.text = email
            self.root.ids.screen_manager.current = "main_screen"
        else:
            label_msg.text = "Email ou mot de passe incorrect."

    # ------------------- Date Picker -------------------
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
                container.add_widget(OneLineListItem(text=f"{p['nom']} ({p['date']})"))

    def valider_dates(self):
        if self.start_date and self.end_date:
            self.filter_prestations_range(self.start_date, self.end_date)
            print(f"Start date : {self.start_date} | End date : {self.end_date}")
        else:
            print("Aucune date sélectionnée !")

    # ------------------- Onglet Recherche -------------------
    def afficher_recherche_template(self):
        upcoming = [
            {"titre": "Installation A", "date": "2026-04-10", "info": "Client X"},
            {"titre": "Réparation B", "date": "2026-04-12", "info": "Client Y"},
            {"titre": "Maintenance C", "date": "2026-04-15", "info": "Client Z"},
        ]
        history = [
            {"titre": "Audit D", "date": "2026-03-10", "info": "Client W"},
            {"titre": "Installation E", "date": "2026-03-15", "info": "Client V"},
            {"titre": "Réparation F", "date": "2026-03-20", "info": "Client U"},
        ]

        self.root.ids.upcoming_container.clear_widgets()
        self.root.ids.history_container.clear_widgets()

        def create_block(data):
            card = MDCard()
            card.orientation = "vertical"
            card.padding = dp(10)
            card.size_hint = (1, None)
            card.height = dp(120)
            card.ripple = True
            card.radius = [10]
            card.md_bg_color = (0.98, 0.98, 0.98, 1)

            card.add_widget(MDLabel(text=f"[b]{data['titre']}[/b]", markup=True, font_style="H6"))
            card.add_widget(MDLabel(text=f"Date : {data['date']}", font_style="Body1"))
            card.add_widget(MDLabel(text=f"Info : {data['info']}", font_style="Body2"))

            # Hover animation
            def hover(dt):
                x, y = Window.mouse_pos
                y = Window.height - y
                if card.collide_point(x, y):
                    Animation(md_bg_color=(0.41,0.11,0.2,1), d=0.2).start(card)
                else:
                    Animation(md_bg_color=(0.98,0.98,0.98,1), d=0.2).start(card)
            Clock.schedule_interval(hover, 0.05)
            return card

        for item in upcoming:
            self.root.ids.upcoming_container.add_widget(create_block(item))
        for item in history:
            self.root.ids.history_container.add_widget(create_block(item))

    # ------------------- Mot de passe -------------------
    def show_change_password_screen(self):
        self.root.ids.screen_manager.current = "change_password_screen"

    def check_fields_mdp(self):
        current = self.root.ids.current_password.text
        newp = self.root.ids.new_password.text
        confirm = self.root.ids.confirm_password.text
        self.root.ids.valider_mdp.disabled = not (current and newp and confirm)

    def valider_mdp(self):
        current = self.root.ids.current_password.text
        newp = self.root.ids.new_password.text
        confirm = self.root.ids.confirm_password.text

        if newp != confirm:
            print("Les mots de passe ne correspondent pas !")
            return

        print("Mot de passe changé avec succès !")
        self.root.ids.current_password.text = ""
        self.root.ids.new_password.text = ""
        self.root.ids.confirm_password.text = ""
        self.root.ids.valider_mdp.disabled = True

        # Retour à l’écran Profil
        self.root.ids.screen_manager.current = "main_screen"
        self.root.ids.nav_bar.switch_tab('profil')


if __name__ == "__main__":
    MyApp().run()