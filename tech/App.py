from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivy.metrics import dp
from datetime import datetime


class MyApp(MDApp):

    def build(self):
        self.start_date = None
        self.end_date = None
        self.media_files = []
        return Builder.load_file("interface_design.kv")

    def on_start(self):
        self.load_all_prestations()

        self.root.ids.current_password.bind(text=lambda *x: self.check_fields_mdp())
        self.root.ids.new_password.bind(text=lambda *x: self.check_fields_mdp())
        self.root.ids.confirm_password.bind(text=lambda *x: self.check_fields_mdp())

    def get_prestations(self, type_prestation):
        # Ajout d'une clé 'type' pour différencier les listes dans open_detail_screen
        data = {
            "historique": [
                {"titre": "Audit sécurité", "info": "10/03/2026", "type": "historique"},
                {"titre": "Installation fibre", "info": "12/03/2026", "type": "historique"},
                {"titre": "Réparation box", "info": "15/03/2026", "type": "historique"},
            ],
            "en_cours": [
                {"titre": "Maintenance serveur", "info": "Aujourd'hui", "type": "en_cours"},
                {"titre": "Installation réseau", "info": "Client Dupont", "type": "en_cours"},
            ],
            "a_venir": [
                {"titre": "Audit IT", "info": "20/04/2026", "type": "a_venir"},
                {"titre": "Upgrade système", "info": "22/04/2026", "type": "a_venir"},
            ]
        }
        return data.get(type_prestation, [])

    def create_prestation_item(self, data):
        card = MDCard(
            orientation="horizontal",
            size_hint=(1, None),
            height=dp(65),
            radius=[12],
            elevation=2,
            padding=dp(8),
            md_bg_color=(1, 1, 1, 1)
        )

        text_layout = MDBoxLayout(orientation="vertical", spacing=dp(2))

        text_layout.add_widget(MDLabel(
            text=data["titre"],
            font_style="Body1",
            bold=True
        ))

        text_layout.add_widget(MDLabel(
            text=data["info"],
            font_style="Caption",
            theme_text_color="Secondary"
        ))

        menu_btn = MDIconButton(icon="dots-vertical")
        menu_btn.bind(on_release=lambda x: self.open_detail_screen(data))

        card.add_widget(text_layout)
        card.add_widget(menu_btn)

        return card

    def load_all_prestations(self):
        # Correction des IDs pour correspondre au KV (container_prestations vs history_container)
        container_h = self.root.ids.container_prestations
        container_h.clear_widgets()
        for item in self.get_prestations("historique"):
            container_h.add_widget(self.create_prestation_item(item))

        container_c = self.root.ids.container_en_cours
        container_c.clear_widgets()
        for item in self.get_prestations("en_cours"):
            container_c.add_widget(self.create_prestation_item(item))

        container_a = self.root.ids.upcoming_container
        container_a.clear_widgets()
        for item in self.get_prestations("a_venir"):
            container_a.add_widget(self.create_prestation_item(item))

    def open_detail_screen(self, data):
        # Données dynamiques (Le numéro 123 pourra venir de ta base SQL plus tard)
        self.current_prestation = {
            "numero": "123", 
            "titre": data["titre"],
            "status": "En cours" if data.get("type") == "en_cours" else "À venir" if data.get("type") == "a_venir" else "Terminé",
            "client": "Jean-Michel Test",
            "technicien": "Jean-Pierre Test",
            "prestation": data["titre"],
            "date_debut": "12/12/2025 13h00",
            "date_fin": "Renseigner" if data.get("type") == "en_cours" else "À définir",
            "adresse": "13 rue du hamburger",
            "complement": "Appartement 12",
            "infos": "J’ai 3 chênes massifs qui bloquent mon jardin"
        }

        # Injection des textes dans les nouveaux IDs du KV Design
        ids = self.root.ids
        ids.detail_title.text = f"Prestation n°{self.current_prestation['numero']}"
        ids.detail_subtitle.text = self.current_prestation["titre"]
        ids.detail_status.text = f"({self.current_prestation['status']})"
        ids.detail_client.text = self.current_prestation["client"]
        ids.detail_technicien.text = self.current_prestation["technicien"]
        ids.detail_prestation.text = self.current_prestation["prestation"]
        ids.detail_date_debut.text = self.current_prestation["date_debut"]
        ids.detail_date_fin.text = self.current_prestation["date_fin"]
        ids.detail_adresse.text = self.current_prestation["adresse"]
        ids.detail_complement.text = self.current_prestation["complement"]
        ids.detail_infos.text = self.current_prestation["infos"]

        # Gestion du bouton "Ajouter un retour"
        if data.get("type") == "en_cours":
            ids.btn_retour.opacity = 1
            ids.btn_retour.disabled = False
        else:
            ids.btn_retour.opacity = 0
            ids.btn_retour.disabled = True

        self.root.ids.screen_manager.current = "detail_screen"

    def go_to_feedback_form(self):
        self.media_files = []
        self.root.ids.feedback_description.text = ""
        self.root.ids.screen_manager.current = "feedback_screen"

    def add_media(self):
        print("Ajout média simulé")
        self.media_files.append("media_test")

    def submit_feedback(self):
        description = self.root.ids.feedback_description.text
        if not description:
            return
        self.save_feedback_to_db(description, self.media_files)
        self.media_files = []
        self.root.ids.feedback_description.text = ""
        self.root.ids.screen_manager.current = "main_screen"
        self.root.ids.nav_bar.switch_tab('prestation_en_cours')

    def cancel_feedback(self):
        self.media_files = []
        self.root.ids.feedback_description.text = ""
        self.root.ids.screen_manager.current = "main_screen"

    def save_feedback_to_db(self, description, media):
        print("INSERT INTO feedback", description, media)

    def tenter_connexion(self, email, mdp):
        label_msg = self.root.ids.login_msg
        label_msg.text = ""
        if not email or not mdp:
            label_msg.text = "Veuillez remplir tous les champs."
            return
        if email == "remi" and mdp == "1234":
            self.root.ids.profil_nom.text = "Remi Kalkan"
            self.root.ids.profil_email.text = email
            self.root.ids.screen_manager.current = "main_screen"
        else:
            label_msg.text = "Email ou mot de passe incorrect."

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
        self.root.ids.valider_mdp.disabled = not (
            self.root.ids.current_password.text and
            self.root.ids.new_password.text and
            self.root.ids.confirm_password.text
        )

    def valider_mdp(self):
        self.root.ids.current_password.text = ""
        self.root.ids.new_password.text = ""
        self.root.ids.confirm_password.text = ""
        self.root.ids.valider_mdp.disabled = True
        self.root.ids.screen_manager.current = "main_screen"


if __name__ == "__main__":
    MyApp().run()