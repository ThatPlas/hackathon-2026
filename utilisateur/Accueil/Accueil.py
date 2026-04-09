from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.card import MDCard
from kivymd.uix.fitimage import FitImage
from kivymd.uix.list import ThreeLineAvatarIconListItem, IconLeftWidget, IconRightWidget
from kivy.metrics import dp
from kivy.properties import StringProperty


class ServiceCard(MDCard):
    image_source = StringProperty("")
    title_text = StringProperty("")
    date_text = StringProperty("")

class ConciergerieApp(MDApp):
    all_services = [
        {"title": "Maintenance", "img": "images/maintenance.jpg", "date": "Mis à jour aujourd'hui"},
        {"title": "Rénovation", "img": "images/renovation.jpg", "date": "Mis à jour hier"},
        {"title": "Entretien", "img": "images/entretien.jpg", "date": "Mis à jour il y a 2 jours"},
        {"title": "Espaces verts", "img": "images/espacesverts.jpg", "date": "Mis à jour aujourd'hui"},
    ]

    def build(self):
        self.theme_cls.primary_palette = "Red"
        self.theme_cls.theme_style = "Light"
        return Builder.load_file("Accueil.kv")

    def on_start(self):
        page_accueil = Builder.load_file("Accueil.kv")
        self.root.ids.content_accueil.add_widget(page_accueil)

        self.filter_services("") 

        try:
            list_view = self.root.ids.prestations_list
            for i in range(3):
                item = ThreeLineAvatarIconListItem(
                    text=f"Prestation {i+1}",
                    secondary_text="Historique d'intervention",
                    tertiary_text="Terminé"
                )
                item.add_widget(IconLeftWidget(icon="clock-outline"))
                list_view.add_widget(item)
        except Exception:
            pass

    def filter_services(self, query=""):
        container = self.root.ids.container_prestations
        container.clear_widgets()

        for service in self.all_services:
            if query.lower() in service["title"].lower():
                card = ServiceCard(
                    image_source=service["img"],
                    title_text=service["title"],
                    date_text=service["date"]
                )
                container.add_widget(card)

if __name__ == '__main__':
    ConciergerieApp().run()