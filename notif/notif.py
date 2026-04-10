from kivymd.uix.screen import MDScreen
from kivymd.uix.list import ThreeLineAvatarIconListItem, IconLeftWidget, OneLineListItem
from kivy.lang import Builder
import Database as bdd
from datetime import datetime

class NotifScreen(MDScreen):
    def on_enter(self):
        """
        Cette méthode s'exécute automatiquement quand on affiche l'écran.
        Elle rafraîchit la liste à chaque fois qu'on clique sur la cloche.
        """
        self.charger_notifications()

    def charger_notifications(self):
        from kivy.app import App
        main_app = App.get_running_app()
        
        # Récupération de l'ID utilisateur (depuis login.py)
        if main_app.utilisateur_courant:
            user_id = main_app.utilisateur_courant['id_user']
        else:
            user_id = 1 # Valeur de secours

        # Sécurité : on vérifie que l'ID notif_list existe bien dans le KV
        container = self.ids.get('notif_list')
        if not container:
            print("Erreur : l'ID 'notif_list' n'est pas encore prêt ou absent du KV.")
            return

        container.clear_widgets()

        try:
            # Appel à la base de données
            notifications = bdd.get_notifs(user_id)

            if not notifications:
                container.add_widget(
                    OneLineListItem(text="Aucune notification pour le moment")
                )
            else:
                for n in notifications:
                    # Correction du nom de colonne : 'date_message' selon ton SQL
                    dt = n.get('date_message', datetime.now())
                    date_str = dt.strftime("%d/%m/%Y à %H:%M") if isinstance(dt, datetime) else str(dt)

                    # Création de l'élément de liste
                    item = ThreeLineAvatarIconListItem(
                        text="Message de la Conciergerie",
                        secondary_text=n.get('message', 'Pas de contenu'),
                        tertiary_text=f"Reçu le {date_str}"
                    )
                    
                    # Icône à gauche
                    item.add_widget(IconLeftWidget(icon="bell-outline"))
                    
                    # Ajout à la liste
                    container.add_widget(item)

        except Exception as e:
            print(f"Erreur fatale chargement notifs : {e}")
            container.add_widget(
                OneLineListItem(text="Erreur lors de la récupération des données")
            )