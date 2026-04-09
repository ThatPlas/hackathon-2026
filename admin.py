import Database
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import TwoLineAvatarIconListItem, OneLineListItem, ImageLeftWidget, IconRightWidget
from kivymd.uix.menu import MDDropdownMenu
from kivy.properties import NumericProperty

KV = '''
ScreenManager:
    id: screen_manager
    
    # ---------------------------------------------------
    # APERÇU RAPIDE & MENU DU BAS
    # ---------------------------------------------------
    MDScreen:
        name: "main_admin"
        
        MDBottomNavigation:
            text_color_active: 0.5, 0, 0.2, 1 
            
            # 1. Onglet Techniciens (Toute la liste)
            MDBottomNavigationItem:
                name: 'nav_techs'
                text: 'Techniciens'
                icon: 'account-group'
                on_tab_press: app.charger_tous_les_techniciens()
                
                MDBoxLayout:
                    orientation: 'vertical'
                    MDRelativeLayout:
                        size_hint_y: None
                        height: "80dp"
                        MDLabel:
                            text: "Tous les techniciens"
                            font_style: "H4"
                            bold: True
                            x: "20dp"
                        # BOUTON POUR AJOUTER UN TECHNICIEN
                        MDIconButton:
                            icon: "plus"
                            pos_hint: {"center_y": .5, "right": 0.95}
                            on_release: app.root.current = "ajouter_tech"

                    MDScrollView:
                        MDList:
                            id: list_all_techs
                            padding: "10dp"

            # 2. Onglet Aperçu rapide (Les 5 derniers)
            MDBottomNavigationItem:
                name: 'nav_apercu'
                text: 'Aperçu rapide'
                icon: 'folder-outline'
                on_tab_press: app.charger_apercu_rapide()
                
                MDBoxLayout:
                    orientation: 'vertical'
                    MDRelativeLayout:
                        size_hint_y: None
                        height: "80dp"
                        MDLabel:
                            text: "Aperçu rapide"
                            font_style: "H4"
                            bold: True
                            x: "20dp"

                    MDScrollView:
                        MDBoxLayout:
                            orientation: 'vertical'
                            adaptive_height: True
                            padding: "20dp"
                            spacing: "20dp"
                            
                            MDLabel:
                                text: "5 derniers techniciens"
                                font_style: "H6"
                                bold: True
                                adaptive_height: True
                            MDList:
                                id: list_last_techs
                                
                            MDLabel:
                                text: "Prestations en attente"
                                font_style: "H6"
                                bold: True
                                adaptive_height: True
                            MDList:
                                id: list_attente
                                
                            MDLabel:
                                text: "Prestations confirmées"
                                font_style: "H6"
                                bold: True
                                adaptive_height: True
                            MDList:
                                id: list_confirmees
                                
                            MDLabel:
                                text: "Prestations terminées"
                                font_style: "H6"
                                bold: True
                                adaptive_height: True
                            MDList:
                                id: list_terminees

    # ---------------------------------------------------
    # DÉTAILS PRESTATION
    # ---------------------------------------------------
    MDScreen:
        name: "detail_presta"
        MDBoxLayout:
            orientation: 'vertical'
            padding: "20dp"
            spacing: "10dp"
            
            MDIconButton:
                icon: "arrow-left"
                on_release: app.root.current = "main_admin"
                
            MDLabel:
                id: dp_titre
                text: "Prestation n°..."
                font_style: "H4"
                bold: True
                adaptive_height: True
            
            MDLabel:
                id: dp_status
                text: "Status..."
                markup: True
                adaptive_height: True
                
            MDLabel:
                id: dp_client
                text: "Client : ..."
                adaptive_height: True
                
            MDLabel:
                id: dp_dates
                text: "Dates : ..."
                adaptive_height: True
                
            MDLabel:
                id: dp_adresse
                text: "Adresse : ..."
                adaptive_height: True
                
            Widget: 
            
            MDBoxLayout:
                adaptive_height: True
                spacing: "20dp"
                MDRaisedButton:
                    id: btn_assigner
                    text: "Assigner un technicien"
                    md_bg_color: 0.2, 0.5, 0.8, 1
                    on_release: app.ouvrir_assignation()
                
                MDRaisedButton:
                    id: btn_accepter
                    text: "Accepter"
                    md_bg_color: 0.1, 0.6, 0.1, 1

    # ---------------------------------------------------
    # DÉTAILS TECHNICIEN
    # ---------------------------------------------------
    MDScreen:
        name: "detail_tech"
        MDBoxLayout:
            orientation: 'vertical'
            padding: "20dp"
            spacing: "15dp"
            
            MDIconButton:
                icon: "arrow-left"
                on_release: app.root.current = "main_admin"
                
            MDBoxLayout:
                adaptive_height: True
                spacing: "20dp"
                MDIcon:
                    icon: "account-circle"
                    font_size: "80dp"
                MDBoxLayout:
                    orientation: 'vertical'
                    MDLabel:
                        id: dt_nom
                        text: "Nom du tech"
                        font_style: "H4"
                        bold: True
                    MDLabel:
                        id: dt_email
                        text: "Email"
                        
            MDLabel:
                text: "Dernières prestations"
                font_style: "H6"
                bold: True
                adaptive_height: True
                
            MDScrollView:
                MDList:
                    id: dt_list_prestas

    # ---------------------------------------------------
    # AJOUTER TECHNICIEN (Formulaire)
    # ---------------------------------------------------
    MDScreen:
        name: "ajouter_tech"
        MDBoxLayout:
            orientation: 'vertical'
            padding: "20dp"
            spacing: "15dp"
            
            MDRelativeLayout:
                size_hint_y: None
                height: "60dp"
                MDIconButton:
                    icon: "arrow-left"
                    pos_hint: {"center_y": .5}
                    on_release: app.root.current = "main_admin"
                MDLabel:
                    text: "Ajouter un technicien"
                    font_style: "H5"
                    bold: True
                    pos_hint: {"center_y": .5}
                    x: "50dp"

            MDTextField:
                id: input_nom
                hint_text: "Nom"
            MDTextField:
                id: input_prenom
                hint_text: "Prénom"
            MDTextField:
                id: input_email
                hint_text: "Adresse e-mail"
            MDTextField:
                id: input_tel
                hint_text: "Téléphone"
            MDTextField:
                id: input_mdp
                hint_text: "Mot de passe provisoire"
                password: True
                
            Widget:
            
            MDRaisedButton:
                text: "Enregistrer"
                pos_hint: {"center_x": .5}
                md_bg_color: 0.1, 0.6, 0.1, 1
                on_release: app.sauvegarder_technicien()

    # ---------------------------------------------------
    # ASSIGNER TECHNICIEN (Liste de sélection)
    # ---------------------------------------------------
    MDScreen:
        name: "assigner_tech"
        MDBoxLayout:
            orientation: 'vertical'
            
            MDRelativeLayout:
                size_hint_y: None
                height: "60dp"
                MDIconButton:
                    icon: "arrow-left"
                    pos_hint: {"center_y": .5}
                    on_release: app.root.current = "detail_presta"
                MDLabel:
                    text: "Sélectionner un technicien"
                    font_style: "H5"
                    bold: True
                    pos_hint: {"center_y": .5}
                    x: "50dp"
                    
            MDScrollView:
                MDList:
                    id: list_techs_dispo
'''

class AdminApp(MDApp):
    presta_actuelle_id = NumericProperty(None) # Mémorise la prestation qu'on est en train de consulter

    def build(self):
        self.theme_cls.primary_palette = "Gray"
        return Builder.load_string(KV)

    def on_start(self):
        self.charger_apercu_rapide()

    def creer_list_item(self, titre, sous_titre, action_menu):
        item = TwoLineAvatarIconListItem(text=titre, secondary_text=sous_titre, bg_color=(1, 1, 1, 1))
        item.add_widget(ImageLeftWidget(source=""))
        btn = IconRightWidget(icon="dots-vertical")
        btn.bind(on_release=lambda x, inst=btn: action_menu(inst))
        item.add_widget(btn)
        return item

    # --- CHARGEMENT DEPUIS Database.py ---
    def charger_apercu_rapide(self):
        self.root.ids.list_last_techs.clear_widgets()
        for tech in Database.get_last_5_techs():
            item = self.creer_list_item(f"{tech['prenom']} {tech['nom']}", "Technicien", 
                                        lambda inst, tid=tech['id_user']: self.ouvrir_menu_tech(inst, tid))
            self.root.ids.list_last_techs.add_widget(item)

        status_mapping = {
            "En attente": self.root.ids.list_attente,
            "Confirmée": self.root.ids.list_confirmees,
            "Terminée": self.root.ids.list_terminees
        }
        for status, widget in status_mapping.items():
            widget.clear_widgets()
            for p in Database.get_last_5_prestas_by_status(status):
                item = self.creer_list_item(f"Prestation n°{p['id_presta']}", p['adresse'], 
                                            lambda inst, pid=p['id_presta']: self.ouvrir_menu_presta(inst, pid))
                widget.add_widget(item)

    def charger_tous_les_techniciens(self):
        self.root.ids.list_all_techs.clear_widgets()
        for tech in Database.get_all_techs():
            item = self.creer_list_item(f"{tech['prenom']} {tech['nom']}", "Technicien", 
                                        lambda inst, tid=tech['id_user']: self.ouvrir_menu_tech(inst, tid))
            self.root.ids.list_all_techs.add_widget(item)

    # --- MENUS DÉROULANTS ---
    def ouvrir_menu_tech(self, button, tech_id):
        menu_items = [{"viewclass": "OneLineListItem", "text": "Voir les détails", 
                       "on_release": lambda: self.aller_vers_detail_tech(tech_id)}]
        self.menu = MDDropdownMenu(caller=button, items=menu_items, width_mult=4)
        self.menu.open()

    def ouvrir_menu_presta(self, button, presta_id):
        menu_items = [{"viewclass": "OneLineListItem", "text": "Voir les détails", 
                       "on_release": lambda: self.aller_vers_detail_presta(presta_id)}]
        self.menu = MDDropdownMenu(caller=button, items=menu_items, width_mult=4)
        self.menu.open()

    # --- NAVIGATION ET DÉTAILS ---
    def aller_vers_detail_tech(self, tech_id):
        self.menu.dismiss()
        tech = Database.get_tech_details(tech_id)
        self.root.ids.dt_nom.text = f"{tech['prenom']} {tech['nom']}"
        self.root.ids.dt_email.text = tech['email']
        
        # NOUVEAU : On charge l'historique des prestations de ce technicien
        self.root.ids.dt_list_prestas.clear_widgets()
        prestas_tech = Database.get_tech_latest_prestas(tech_id)
        if prestas_tech:
            for p in prestas_tech:
                item = TwoLineAvatarIconListItem(text=f"Prestation n°{p['id_presta']} ({p['status']})", secondary_text=p['adresse'])
                self.root.ids.dt_list_prestas.add_widget(item)
        else:
            self.root.ids.dt_list_prestas.add_widget(OneLineListItem(text="Aucune prestation pour le moment."))
            
        self.root.current = "detail_tech"

    def aller_vers_detail_presta(self, presta_id):
        self.menu.dismiss()
        self.presta_actuelle_id = presta_id # On mémorise l'ID
        p = Database.get_presta_details(presta_id)
        
        self.root.ids.dp_titre.text = f"Prestation n°{p['id_presta']}"
        color = "red" if p['status'] == "En attente" else "green" if p['status'] == "Confirmée" else "gray"
        self.root.ids.dp_status.text = f"[color={color}]({p['status']})[/color]"
        self.root.ids.dp_client.text = f"Client : {p['client_prenom']} {p['client_nom']}"
        self.root.ids.dp_dates.text = f"Début : {p['debut_contrat']}"
        self.root.ids.dp_adresse.text = f"Adresse : {p['adresse']}"
        
        # Le bouton d'assignation n'est visible que si elle n'est pas terminée
        show_btn = p['status'] != "Terminée"
        self.root.ids.btn_assigner.opacity = 1 if show_btn else 0
        self.root.ids.btn_assigner.disabled = not show_btn
        
        self.root.current = "detail_presta"

    # --- NOUVELLES ACTIONS : AJOUT ET ASSIGNATION ---
    def sauvegarder_technicien(self):
        nom = self.root.ids.input_nom.text
        prenom = self.root.ids.input_prenom.text
        email = self.root.ids.input_email.text
        tel = self.root.ids.input_tel.text
        mdp = self.root.ids.input_mdp.text
        
        if nom and prenom and email:
            succes = Database.add_technicien(nom, prenom, email, tel, mdp)
            if succes:
                # On vide les champs
                self.root.ids.input_nom.text = ""
                self.root.ids.input_prenom.text = ""
                self.root.ids.input_email.text = ""
                self.root.ids.input_tel.text = ""
                self.root.ids.input_mdp.text = ""
                # On recharge les listes et on retourne à l'accueil
                self.charger_tous_les_techniciens()
                self.charger_apercu_rapide()
                self.root.current = "main_admin"

    def ouvrir_assignation(self):
        """Ouvre la liste des techniciens pour assignation"""
        self.root.ids.list_techs_dispo.clear_widgets()
        techs = Database.get_all_techs()
        
        for tech in techs:
            item = TwoLineAvatarIconListItem(text=f"{tech['prenom']} {tech['nom']}", secondary_text="Cliquer pour assigner")
            # Au clic, ça assigne ce technicien à la prestation actuelle
            item.bind(on_release=lambda x, tid=tech['id_user']: self.confirmer_assignation(tid))
            self.root.ids.list_techs_dispo.add_widget(item)
            
        self.root.current = "assigner_tech"

    def confirmer_assignation(self, tech_id):
        """Action déclenchée quand on clique sur un technicien dans la liste"""
        if self.presta_actuelle_id:
            Database.assign_tech_to_presta(self.presta_actuelle_id, tech_id)
            self.charger_apercu_rapide() # Mise à jour de l'accueil
            self.aller_vers_detail_presta(self.presta_actuelle_id) # Retour au détail actualisé

if __name__ == "__main__":
    AdminApp().run()