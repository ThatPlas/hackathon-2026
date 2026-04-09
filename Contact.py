from kivymd.app import MDApp
from kivy.lang import Builder
import os

class ContactApp(MDApp):
    kv_file = None 

    def build(self):
        self.theme_cls.primary_palette = "Red"
        
        return Builder.load_file("contact.kv")

    def envoyer_contact(self, nom, email, message):
        if not nom or not email or not message:
            print("Erreur : Champs obligatoires vides")
            return
        
        print(f"Message de {nom} ({email}) : {message}")

    def retour_accueil(self):
        print("Retour à l'accueil")

if __name__ == "__main__":
    ContactApp().run()