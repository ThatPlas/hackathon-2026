import sys
import os

chemin_racine = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if chemin_racine not in sys.path:
    sys.path.append(chemin_racine)

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.properties import NumericProperty, StringProperty

try:
    from Database import create_avis 
except ImportError:
    print("Erreur : Impossible de trouver Database.py.")

class AvisScreen(Screen):
    # Les variables qui seront injectées quand on clique sur la notification
    id_presta = NumericProperty(0)
    service_nom = StringProperty("")
    tech_nom = StringProperty("")
    date_presta = StringProperty("")
    image_path = StringProperty("")

    def soumettre_avis(self):
        message_text = self.ids.input_message.text

        if not message_text.strip():
            self.afficher_message("Veuillez écrire un message.", erreur=True)
            return
            
        if self.id_presta == 0:
            self.afficher_message("Erreur : Prestation introuvable.", erreur=True)
            return

        try:
            # Envoi à la base de données
            create_avis(self.id_presta, message_text)
            
            # Succès
            self.afficher_message("Merci ! Avis envoyé.", erreur=False)
            self.ids.input_message.text = ""
            
        except Exception as e:
            self.afficher_message("Erreur lors de l'envoi.", erreur=True)
            print(f"Erreur SQL : {e}")

    def afficher_message(self, texte, erreur=False):
        label = self.ids.message_retour
        label.text = texte
        if erreur:
            label.color = (0.8, 0, 0, 1) # Rouge
        else:
            label.color = (0, 0.6, 0, 1) # Vert


class MonApplicationTest(App):
    def build(self):
        kv_path = os.path.join(os.path.dirname(__file__), 'avis.kv')
        Builder.load_file(kv_path)
        
        sm = ScreenManager()
        
        ecran_avis = AvisScreen(name='avis')
        
        # --- DONNÉES INJECTÉES POUR LE TEST (Celles de votre maquette) ---
        ecran_avis.id_presta = 1 
        ecran_avis.service_nom = "Ménage régulier"
        ecran_avis.tech_nom = "Océane"
        ecran_avis.date_presta = "04/09/2026"
        # On utilise l'image d'entretien présente dans votre dossier images
        ecran_avis.image_path = "../../images/entretien.jpg" 
        
        sm.add_widget(ecran_avis)
        return sm

if __name__ == '__main__':
    MonApplicationTest().run()