from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivy.uix.image import Image
from kivymd.uix.fitimage import FitImage
from kivy.metrics import dp

# --- LE DESIGN (KV) ---
# Nous définissons toute l'interface ici pour plus de clarté
interface_design = """
MDScreen:
    MDBottomNavigation:
        # Couleurs personnalisées basées sur votre maquette
        panel_color: "#F7F5F5" # Gris très clair pour le fond du menu
        text_color_active: "#691C32" # Bordeaux du logo pour l'élément actif

        # --- PAGE RECHERCHE (simplifiée pour l'instant) ---
        MDBottomNavigationItem:
            name: 'page_recherche'
            text: 'Rechercher'
            icon: 'magnify'
            MDLabel:
                text: 'Page de Recherche (à venir)'
                halign: 'center'

        # --- PAGE ACCUEIL (votre maquette principale) ---
        MDBottomNavigationItem:
            name: 'page_accueil'
            text: 'Accueil'
            icon: 'home-outline'
            
            # Contenu défilant pour la page d'accueil
            MDScrollView:
                do_scroll_x: False  # Pas de défilement horizontal
                
                MDBoxLayout:
                    orientation: 'vertical'
                    adaptive_height: True  # La hauteur s'adapte au contenu
                    padding: [dp(20), dp(10), dp(20), dp(20)] # Marges [gauche, haut, droite, bas]
                    spacing: dp(15)        # Espace entre les éléments

                    # LOGO (tout en haut, centré)
                    # REMPLACEZ 'logo.png' PAR LE CHEMIN RÉEL DE VOTRE LOGO
                    Image:
                        source: 'logo.png' 
                        size_hint_y: None
                        height: dp(80)  # Hauteur fixe
                        pos_hint: {'center_x': 0.5}

                    # TITRE PRINCIPAL
                    MDLabel:
                        text: 'Nos prestations'
                        font_style: 'H5'
                        theme_text_color: 'Primary'
                        bold: True
                        size_hint_y: None
                        height: self.texture_size[1] # Hauteur s'adapte au texte

                    # -- CARTES DE SERVICE -- (Utilisation d'un composant réutilisable défini plus bas)

                    # Maintenance
                    # REMPLACEZ 'images/maintenance.jpg' PAR VOTRE IMAGE
                    ServiceCard:
                        image_source: 'images/maintenance.jpg'
                        title_text: 'Maintenance'
                        date_text: 'Mis à jour aujourd\\'hui'

                    # Rénovation
                    # REMPLACEZ 'images/renovation.jpg' PAR VOTRE IMAGE
                    ServiceCard:
                        image_source: 'images/renovation.jpg'
                        title_text: 'Rénovation'
                        date_text: 'Mis à jour hier'

                    # Entretien
                    # REMPLACEZ 'images/entretien.jpg' PAR VOTRE IMAGE
                    ServiceCard:
                        image_source: 'images/entretien.jpg'
                        title_text: 'Entretien'
                        date_text: 'Mis à jour il y a 2 jours'

                    # Espaces verts
                    # REMPLACEZ 'images/espaces_verts.jpg' PAR VOTRE IMAGE
                    ServiceCard:
                        image_source: 'images/espaces_verts.jpg'
                        title_text: 'Espaces verts'
                        date_text: 'Mis à jour aujourd\\'hui'

        # --- PAGE PROFIL (simplifiée pour l'instant) ---
        MDBottomNavigationItem:
            name: 'page_profil'
            text: 'Profil'
            icon: 'account-outline'
            MDLabel:
                text: 'Page Profil (à venir)'
                halign: 'center'

# DÉFINITION D'UNE CARTE DE SERVICE RÉUTILISABLE
# Cela simplifie le code principal et assure la cohérence du design
<ServiceCard@MDCard>:
    orientation: 'vertical'
    size_hint_y: None
    height: dp(220)  # Hauteur totale fixe de la carte
    elevation: 2     # Ombre légère
    radius: [dp(15), dp(15), dp(15), dp(15)] # Bords arrondis partout
    padding: dp(10)
    md_bg_color: 1, 1, 1, 1 # Fond blanc
    ripple_behavior: True # Effet visuel au clic
    
    # Propriétés personnalisées pour passer dynamiquement l'image et les textes
    image_source: ''
    title_text: ''
    date_text: ''

    # L'image qui s'adapte parfaitement avec des bords arrondis en haut
    FitImage:
        source: root.image_source
        size_hint_y: None
        height: dp(140) # Hauteur de l'image
        radius: [dp(15), dp(15), 0, 0] # Arrondi uniquement en haut

    # Conteneur pour les textes en dessous de l'image
    MDBoxLayout:
        orientation: 'vertical'
        padding: [dp(5), dp(5), 0, 0] # Petites marges intérieures
        spacing: dp(2)
        
        MDLabel:
            text: root.title_text
            font_style: 'Subtitle1'
            theme_text_color: 'Primary'
            bold: True
            size_hint_y: None
            height: self.texture_size[1]

        MDLabel:
            text: root.date_text
            font_style: 'Caption'
            theme_text_color: 'Secondary' # Texte plus clair
            size_hint_y: None
            height: self.texture_size[1]

"""

# --- LA LOGIQUE (PYTHON) ---

class ConciergerieApp(MDApp):
    def build(self):
        # Définition du thème global
        self.theme_cls.primary_palette = "Red" # Palette bordeaux proche de votre logo
        self.theme_cls.theme_style = "Light"      # Thème clair
        
        # Chargement et retour de l'interface définie en KV
        return Builder.load_string(interface_design)

# Point d'entrée de l'application
if __name__ == '__main__':
    # Assurez-vous d'avoir installé kivymd : pip install kivymd
    ConciergerieApp().run()