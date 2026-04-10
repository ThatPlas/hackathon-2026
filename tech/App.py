from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivy.metrics import dp
from datetime import datetime

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import Database

class MyApp(MDApp):

    def build(self):
        self.current_user_id = 1
        self.current_prestat_id = None
        self.start_date = None
        self.end_date = None
        self.media_files = []
        return Builder.load_file("interface_design.kv")

    def on_start(self):
        if self.current_user_id:
            self.load_all_prestations()

        self.root.ids.current_password.bind(text=lambda *x: self.check_fields_mdp())
        self.root.ids.new_password.bind(text=lambda *x: self.check_fields_mdp())
        self.root.ids.confirm_password.bind(text=lambda *x: self.check_fields_mdp())

    def load_all_prestations(self):
        self.update_container("upcoming_container", "confirmée")
        self.update_container("container_en_cours", "en_cours")
        self.update_container("container_prestations", "terminée")

    def update_container(self, container_id, status):
        container = self.root.ids[container_id]
        container.clear_widgets()
        prestations = Database.get_prestations_by_status_for_tech(self.current_user_id, status)
        for p in prestations:
            data = {
                "id": p["titre"],
                "titre": p["type_nom"],
                "info": p["date_presta"],
                "type": status
            }
            container.add_widget(self.create_prestation_item(data))

    def create_prestation_item(self, data):
        card = MDCard(orientation="vertical", padding=dp(10), size_hint=(1, None), height=dp(100), ripple_behavior=True, md_bg_color=(0.95, 0.95, 0.95, 1))
        card.bind(on_release=lambda x: self.open_detail_screen(data))
        card.add_widget(MDLabel(text=f"[b]{data['titre']}[/b]", markup=True, font_style="Subtitle1"))
        card.add_widget(MDLabel(text=f"Prestation #{data['id']}", font_style="Caption", theme_text_color="Hint"))
        card.add_widget(MDLabel(text=f"Date : {data['info']}", font_style="Caption"))
        
        return card

    def open_detail_screen(self, data):
        p = Database.get_presta_details(data["id"])
        self.current_prestation_id = data["id_presta"]

        mappping = {
            "Confirmée": ('detail_a_venir', 'av_'),
            "En cours": ('detail_en_cours', 'ec_'),
            "Terminée": ('detail_historique', 'hi_')
        }
        target_screen, prefix = mappping.get(p["status"], ("detail_historique", "hi_"))

        self.root.ids[f"{prefix}titre"].text = f"Prestation : {p['id_presta']}"
        self.root.ids[f"{prefix}client"].text = f"{p['client_prenom']} {p['client_nom']}"
        self.root.ids[f"{prefix}adresse"].text = p['adresse']
        self.root.ids[f"{prefix}infos"].text = p['info_supp'] if p['info_supp'] else "Aucune information supplémentaire."
        self.root.ids.screen_manager.current = target_screen

    def go_to_feedback_form(self):
        self.root.ids.screen_manager.current = "feedback_screen"
    
    def cancel_feedback(self):
        self.root.ids.feedback_description.text = ""
        self.root.ids.screen_manager.current = "main_screen"

    def submit_feedback(self):
        commentaire = self.root.ids.feedback_description.text
        if commentaire and self.current_prestation_id:
            if Database.add_presta_feedback(self.current_prestation_id, commentaire):
                self.root.ids.feedback_description.text = ""
                self.load_all_prestations()
                self.root.ids.screen_manager.current = "main_screen"


    def show_date_picker(self):
        date_dialog = MDDatePicker(mode="range")
        date_dialog.bind(on_save=self.on_save_date)
        date_dialog.open()

    def on_save_date(self, instance, value, date_range):
        if date_range:
            self.start_date = date_range[0].strftime("%Y-%m-%d")
            self.end_date = date_range[-1].strftime("%Y-%m-%d")
            self.root.ids.field.text = f"{self.start_date} → {self.end_date}"

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

        self.root.ids.current_password.text = ""
        self.root.ids.new_password.text = ""
        self.root.ids.confirm_password.text = ""
        self.root.ids.valider_mdp.disabled = True
        self.root.ids.screen_manager.current = "main_screen"

if __name__ == "__main__":
    MyApp().run()