from kivy.config import Config
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '740')
Config.set('graphics', 'resizable', False)

import calendar as std_calendar
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivymd.uix.button import MDFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.clock import Clock
from datetime import datetime
from kivy.core.window import Window
from kivy.metrics import dp
import sys
import os

# Simulation Database
try:
    import Database
except ImportError:
    class Database:
        @staticmethod
        def get_prestations_by_status_for_tech(uid, status): return []

class MyApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Indigo"
        
        # --- Variables Globales ---
        self.current_user_id = 1
        
        # --- Variables Absence ---
        self.view_month = datetime.now().month
        self.view_year = datetime.now().year
        self.date_debut = None
        self.date_fin = None
        
        return Builder.load_file("interface_design.kv")

    def on_start(self):
        self.load_all_prestations()
        # Bindings mot de passe
        for f in ['current_password', 'new_password', 'confirm_password']:
            if f in self.root.ids:
                self.root.ids[f].bind(text=lambda *x: self.check_fields_mdp())

    # --- LOGIQUE PRESTATIONS (Main) ---
    def load_all_prestations(self):
        self.update_container("upcoming_container", "confirmée")
        self.update_container("container_en_cours", "en_cours")
        self.update_container("container_prestations", "terminée")

    def update_container(self, container_id, status):
        if container_id not in self.root.ids: return
        container = self.root.ids[container_id]
        container.clear_widgets()
        prestations = Database.get_prestations_by_status_for_tech(self.current_user_id, status)
        for p in prestations:
            data = {"id": p.get("titre"), "titre": p.get("type_nom"), "info": p.get("date_presta"), "status": status}
            card = MDCard(orientation="vertical", padding=dp(10), size_hint=(1, None), height=dp(100), ripple_behavior=True)
            card.add_widget(MDLabel(text=f"[b]{data['titre']}[/b]", markup=True))
            card.bind(on_release=lambda x, d=data: self.open_detail_screen(d))
            container.add_widget(card)

    def open_detail_screen(self, data):
        self.root.ids.screen_manager.current = "detail_en_cours"

    # --- LOGIQUE ABSENCE (Fusionnée) ---
    def on_absence_tab_press(self):
        """Appelé quand on clique sur l'icône calendrier de la nav bar"""
        Clock.schedule_once(lambda dt: self.update_calendar())

    def switch_absence_screen(self, screen_name, direction="left"):
        self.root.ids.absence_manager.transition.direction = direction
        self.root.ids.absence_manager.current = screen_name
        if screen_name == "liste_absence":
            self.generer_liste_absences()

    def changer_mois(self, direction):
        self.view_month += direction
        if self.view_month > 12:
            self.view_month = 1
            self.view_year += 1
        elif self.view_month < 1:
            self.view_month = 12
            self.view_year -= 1
        self.update_calendar()

    def update_calendar(self):
        if 'calendar_grid' not in self.root.ids: return
        grid = self.root.ids.calendar_grid
        grid.clear_widgets()
        
        today = datetime.now().date()
        self.root.ids.label_mois_annee.text = f"{std_calendar.month_name[self.view_month]} {self.view_year}"
        f_day, num_days = std_calendar.monthrange(self.view_year, self.view_month)
        
        cell_size = (Window.width - dp(60)) / 7

        for _ in range((f_day + 1) % 7):
            grid.add_widget(Widget(size_hint=(None, None), size=(dp(cell_size), dp(cell_size))))

        for i in range(1, num_days + 1):
            curr = datetime(self.view_year, self.view_month, i).date()
            bg, tc = (0,0,0,0), (0,0,0,1)
            is_dis = curr <= today
            
            if is_dis: tc = (0.7, 0.7, 0.7, 1)
            
            if self.date_debut == curr or self.date_fin == curr:
                tc, bg = (1,1,1,1), self.theme_cls.primary_color
            elif self.date_debut and self.date_fin and self.date_debut < curr < self.date_fin:
                tc, bg = (0,0,0,1), (0.8, 0.8, 1, 0.3)

            btn = MDFlatButton(
                text=str(i), theme_text_color="Custom", text_color=tc, md_bg_color=bg,
                size_hint=(None, None), size=(dp(cell_size), dp(cell_size)),
                disabled=is_dis
            )
            btn.bind(on_release=lambda x, d=curr: self.select_absence_date(d))
            grid.add_widget(btn)

    def select_absence_date(self, selected_date):
        if not self.date_debut or (self.date_debut and self.date_fin):
            self.date_debut, self.date_fin = selected_date, None
            self.root.ids.info_selection.text = f"Début : {selected_date.strftime('%d/%m/%Y')}"
        elif selected_date < self.date_debut:
            self.date_debut = selected_date
            self.root.ids.info_selection.text = f"Début : {selected_date.strftime('%d/%m/%Y')}"
        elif selected_date > self.date_debut:
            self.date_fin = selected_date
            self.root.ids.info_selection.text = f"Du {self.date_debut.strftime('%d/%m')} au {self.date_fin.strftime('%d/%m/%Y')}"
        
        self.update_calendar()
        self.root.ids.btn_envoyer_absence.disabled = not (self.date_debut and self.date_fin)

    def envoyer_formulaire_absence(self):
        # Ici tu ajouterais l'appel DB pour sauvegarder l'absence
        self.switch_absence_screen("liste_absence", direction="left")
        self.date_debut = self.date_fin = None
        self.root.ids.motif_input.text = ""
        self.root.ids.info_selection.text = "Sélectionnez une période"
        self.update_calendar()

    def generer_liste_absences(self):
        container = self.root.ids.container_liste_absences
        container.clear_widgets()
        demandes = [
            {"debut": "12/04", "fin": "15/04", "status": "Validé", "color": (0.1, 0.7, 0.1, 1)},
            {"debut": "20/04", "fin": "21/04", "status": "En attente", "color": (0.9, 0.6, 0, 1)},
        ]
        for d in demandes:
            card = MDCard(size_hint_y=None, height=dp(70), padding=dp(15), radius=[dp(15)], elevation=1)
            card.add_widget(MDLabel(text=f"Du {d['debut']} au {d['fin']}", bold=True))
            card.add_widget(MDLabel(text=d['status'], halign="right", theme_text_color="Custom", text_color=d['color']))
            container.add_widget(card)

    # --- AUTRES FONCTIONS ---
    def check_fields_mdp(self):
        ids = self.root.ids
        ids.valider_mdp.disabled = not (ids.current_password.text and ids.new_password.text and ids.confirm_password.text)

    def valider_mdp(self): self.root.ids.screen_manager.current = "main_screen"
    def go_to_feedback_form(self): self.root.ids.screen_manager.current = "feedback_screen"
    def cancel_feedback(self): self.root.ids.screen_manager.current = "main_screen"
    def submit_feedback(self): self.root.ids.screen_manager.current = "main_screen"
    def show_change_password_screen(self): self.root.ids.screen_manager.current = "change_password_screen"

if __name__ == "__main__":
    MyApp().run()