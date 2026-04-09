from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.card import MDCard
from kivymd.uix.fitimage import FitImage
from kivymd.uix.list import ThreeLineAvatarIconListItem, IconLeftWidget, IconRightWidget
from kivy.metrics import dp
from kivy.properties import StringProperty

interface_design = """
MDScreen:
    MDBottomNavigation:
        id: nav_bar
        panel_color: "#F7F5F5"
        text_color_active: "#691C32"

        MDBottomNavigationItem:
            name: 'page_recherche'
            text: 'Rechercher'
            icon: 'magnify'
            
            MDBoxLayout:
                orientation: 'vertical'
                padding: [0, dp(10), 0, 0]
                
                Image:
                    source: 'logo.png' 
                    size_hint_y: None
                    height: dp(60)
                    pos_hint: {'center_x': 0.5}

                MDBoxLayout:
                    adaptive_height: True
                    padding: [dp(20), dp(10), dp(20), dp(10)]
                    MDTextField:
                        id: search_field
                        hint_text: "Rechercher une prestation (ex: Maintenance)"
                        mode: "round"
                        on_text: app.filter_services(self.text)

                MDScrollView:
                    MDBoxLayout:
                        id: container_prestations
                        orientation: 'vertical'
                        adaptive_height: True
                        padding: dp(20)
                        spacing: dp(15)

        MDBottomNavigationItem:
            name: 'page_accueil'
            id: content_accueil
            text: 'Accueil'
            icon: 'home-outline'

        MDBottomNavigationItem:
            name: 'page_profil'
            text: 'Profil'
            icon: 'account'
            MDScrollView:
                MDBoxLayout:
                    orientation: 'vertical'
                    adaptive_height: True
                    padding: dp(20)
                    spacing: dp(20)

                    MDBoxLayout:
                        adaptive_height: True
                        spacing: dp(20)
                        FitImage:
                            source: "profil_logo.png"
                            size_hint: None, None
                            size: dp(120), dp(120)
                            radius: [self.width / 2,]
                        MDLabel:
                            text: "Jean-Michel\\nTest"
                            font_style: "H5"
                            bold: True
                            pos_hint: {"center_y": .5}

                    MDSeparator:

                    MDLabel:
                        text: "Vos dernières prestations"
                        font_style: "H6"
                        bold: True
                        adaptive_height: True

                    MDList:
                        id: prestations_list

<ServiceCard>:
    orientation: 'vertical'
    size_hint_y: None
    height: dp(220)
    elevation: 2
    radius: [dp(15),]
    padding: dp(10)
    md_bg_color: 1, 1, 1, 1
    
    FitImage:
        source: root.image_source
        size_hint_y: None
        height: dp(140)
        radius: [dp(15), dp(15), 0, 0]

    MDBoxLayout:
        orientation: 'vertical'
        padding: [dp(5), dp(5), 0, 0]
        MDLabel:
            text: root.title_text
            font_style: 'Subtitle1'
            bold: True
        MDLabel:
            text: root.date_text
            font_style: 'Caption'
            theme_text_color: 'Secondary'
"""

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
        return Builder.load_string(interface_design)

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