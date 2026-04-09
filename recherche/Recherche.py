from kivy.config import Config
Config.set('kivy', 'metrics_density', '1') 

from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.card import MDCard
from kivymd.uix.list import ThreeLineAvatarIconListItem, IconLeftWidget, OneLineListItem, IconRightWidget
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.label import MDLabel
from kivy.metrics import dp
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
import Database as bdd
from datetime import datetime

Window.size = (360, 740)

interface_design = """
<ServiceCard>:
    orientation: 'vertical'
    size_hint_y: None
    height: header.height + sub_services_list.height
    elevation: 2
    radius: [dp(15),]
    md_bg_color: 1, 1, 1, 1
    on_release: root.toggle_expansion()
    
    MDBoxLayout:
        id: header
        orientation: 'vertical'
        size_hint_y: None
        height: dp(200)
        FitImage:
            source: root.image_source
            size_hint_y: None
            height: dp(140)
            radius: [dp(15), dp(15), 0, 0]
        MDBoxLayout:
            orientation: 'vertical'
            padding: [dp(15), dp(10), dp(15), 0]
            MDLabel:
                text: root.title_text
                font_style: 'Subtitle1'
                bold: True
                adaptive_height: True
            MDLabel:
                text: "Cliquez pour voir les services"
                font_style: 'Caption'
                theme_text_color: 'Secondary'
                adaptive_height: True
    
    MDList:
        id: sub_services_list
        size_hint_y: None
        height: 0
        opacity: 0
        adaptive_height: True
"""

class ServiceCard(MDCard):
    image_source = StringProperty("")
    title_text = StringProperty("")
    expanded = BooleanProperty(False)

    def toggle_expansion(self):
        self.expanded = not self.expanded
        target_height = self.ids.sub_services_list.minimum_height if self.expanded else 0
        target_opacity = 1 if self.expanded else 0
        anim = Animation(height=target_height, opacity=target_opacity, duration=0.2, t='out_quad')
        anim.start(self.ids.sub_services_list)

class ConciergerieApp(MDApp):
    current_service_id = NumericProperty(0)
    user_id = 1

    def build(self):
        self.theme_cls.primary_palette = "Red"
        self.theme_cls.theme_style = "Light"
        self.all_services = bdd.get_categories()
        return Builder.load_file('Recherche.kv')

    def on_start(self):
        self.filter_services("") 

    def filter_services(self, query=""):
        container = self.root.ids.container_prestations
        container.clear_widgets()
        query = query.lower().strip()
        for category in self.all_services:
            cat_name_display = category["nom"].strip()
            cat_name_lower = cat_name_display.lower()
            all_types = bdd.get_type_prestas_by_category(category['id_categorie'])
            matching_types = [t for t in all_types if query in t["nom"].lower()]
            if query == "" or query in cat_name_lower or matching_types:
                card = ServiceCard(image_source=f"images/{cat_name_lower}.jpg", title_text=cat_name_display)
                list_to_show = all_types if (query == "" or query in cat_name_lower) else matching_types
                for p in list_to_show:
                    item = OneLineListItem(text=f"{p['nom']} - {p['prix']}€", divider="Full", on_release=lambda x, data=p: self.ouvrir_details(data))
                    card.ids.sub_services_list.add_widget(item)
                container.add_widget(card)

    def ouvrir_details(self, data):
        self.current_service_id = data['id_type_presta']
        self.root.ids.detail_titre.text = data['nom']
        self.root.ids.detail_desc.text = data['description']
        self.root.ids.detail_prix.text = f"Prix : {data['prix']} €"
        self.root.ids.input_date.text = datetime.now().strftime("%d/%m/%Y")
        self.root.ids.input_hour.text = ""
        self.root.ids.search_screen_manager.transition.direction = "left"
        self.root.ids.search_screen_manager.current = 'details_presta'

    def ouvrir_panier(self):
        self.charger_panier()
        self.root.ids.search_screen_manager.transition.direction = "left"
        self.root.ids.search_screen_manager.current = 'page_panier'

    def charger_panier(self):
        panier_list = self.root.ids.panier_list
        panier_list.clear_widgets()
        items = bdd.get_user_panier(self.user_id)
        total = 0
        for item in items:
            total += float(item['prix'])
            dt = item['debut_contrat']
            date_formatee = dt.strftime("%d/%m/%Y à %Hh%M") if isinstance(dt, datetime) else str(dt)
            row = ThreeLineAvatarIconListItem(text=item['nom'], secondary_text=f"Prix : {item['prix']}€", tertiary_text=f"{date_formatee}")
            row.add_widget(IconLeftWidget(icon="tag-outline"))
            delete_btn = IconRightWidget(icon="trash-can-outline", theme_text_color="Error", on_release=lambda x, id_p=item['id_presta']: self.supprimer_du_panier(id_p))
            row.add_widget(delete_btn)
            panier_list.add_widget(row)
        self.root.ids.total_label.text = f"{total:.2f} €"

    def supprimer_du_panier(self, id_presta):
        try:
            bdd.delete_prestation(id_presta)
            self.charger_panier()
            self.afficher_message("Prestation supprimée", couleur=[1, 0, 0, 1])
        except Exception as e: self.afficher_message(f"Erreur : {e}")

    def ajouter_prestation(self):
        date_txt = self.root.ids.input_date.text.strip()
        heure_txt = self.root.ids.input_hour.text.strip()
        if not date_txt or not heure_txt:
            self.afficher_message("Remplissez la date et l'heure !", couleur=[1, 0, 0, 1])
            return
        try:
            h = int(heure_txt)
            if not (8 <= h <= 16):
                self.afficher_message("L'heure doit être entre 8 et 16", couleur=[1, 0, 0, 1])
                return
            date_obj = datetime.strptime(date_txt, "%d/%m/%Y")
            dt_mysql = date_obj.replace(hour=h, minute=0, second=0).strftime('%Y-%m-%d %H:%M:%S')
            bdd.create_prestation(id_user=self.user_id, id_type_presta=self.current_service_id, debut=dt_mysql, fin=None, adresse="À définir")
            self.afficher_message("Ajouté au panier !")
            self.root.ids.search_screen_manager.transition.direction = "right"
            self.root.ids.search_screen_manager.current = 'liste_recherche'
        except ValueError: self.afficher_message("Format Date ou Heure invalide !", couleur=[1, 0, 0, 1])
        except Exception as e: self.afficher_message(f"Erreur : {str(e)}")

    def payer_commande(self):
        try:
            bdd.valider_panier_db(self.user_id)
            self.charger_panier()
            self.afficher_message("Réservation en attente de validation", couleur=[0, 0.6, 0, 1])
            self.root.ids.search_screen_manager.transition.direction = "right"
            self.root.ids.search_screen_manager.current = 'liste_recherche'
        except Exception as e: self.afficher_message(f"Erreur lors du paiement : {e}")

    def afficher_message(self, texte, couleur=[0.4, 0.1, 0.2, 1]):
        try:
            snackbar = Snackbar(bg_color=couleur)
            label = MDLabel(text=texte, theme_text_color="Custom", text_color=[1, 1, 1, 1], valign="center")
            snackbar.add_widget(label)
            snackbar.open()
        except: print(f"Notification : {texte}")

if __name__ == '__main__':
    ConciergerieApp().run()