import Database
import calendar
from datetime import datetime, date
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import TwoLineAvatarIconListItem, OneLineListItem, ImageLeftWidget, IconRightWidget
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
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

                            MDLabel:
                                text: "Prestations annulées"
                                font_style: "H6"
                                bold: True
                                adaptive_height: True
                            MDList:
                                id: list_annulees

    # ---------------------------------------------------
    # DÉTAILS PRESTATION
    # ---------------------------------------------------
    MDScreen:
        name: "detail_presta"
        MDBoxLayout:
            orientation: 'vertical'

            # Barre du haut
            MDBoxLayout:
                size_hint_y: None
                height: "56dp"
                padding: "4dp"
                MDIconButton:
                    icon: "arrow-left"
                    pos_hint: {"center_y": .5}
                    on_release: app.root.current = "main_admin"
                MDLabel:
                    id: dp_header
                    text: "Détails prestation"
                    font_style: "H6"
                    bold: True
                    pos_hint: {"center_y": .5}

            MDScrollView:
                MDBoxLayout:
                    orientation: 'vertical'
                    adaptive_height: True
                    padding: "20dp"
                    spacing: "6dp"

                    # Titre + Status
                    MDLabel:
                        id: dp_titre
                        text: "Prestation n°..."
                        font_style: "H4"
                        bold: True
                        adaptive_height: True

                    MDBoxLayout:
                        adaptive_height: True
                        spacing: "10dp"
                        MDLabel:
                            id: dp_type_presta
                            text: ""
                            adaptive_height: True
                        MDLabel:
                            id: dp_status
                            text: ""
                            markup: True
                            adaptive_height: True

                    # Séparateur
                    MDSeparator:
                        height: "1dp"

                    # Client
                    MDLabel:
                        text: "Client"
                        font_size: "12sp"
                        theme_text_color: "Secondary"
                        adaptive_height: True
                    MDLabel:
                        id: dp_client
                        text: "..."
                        font_style: "H6"
                        adaptive_height: True

                    # Technicien
                    MDLabel:
                        text: "Technicien"
                        font_size: "12sp"
                        theme_text_color: "Secondary"
                        adaptive_height: True
                    MDLabel:
                        id: dp_technicien
                        text: "Assigner un technicien"
                        markup: True
                        adaptive_height: True
                        on_touch_down: if self.collide_point(*args[1].pos): app.ouvrir_assignation()

                    # Type de prestation
                    MDLabel:
                        text: "Prestation"
                        font_size: "12sp"
                        theme_text_color: "Secondary"
                        adaptive_height: True
                    MDLabel:
                        id: dp_type_detail
                        text: "..."
                        adaptive_height: True

                    # Dates
                    MDBoxLayout:
                        adaptive_height: True
                        spacing: "20dp"
                        MDBoxLayout:
                            orientation: 'vertical'
                            adaptive_height: True
                            MDLabel:
                                text: "Date et heure début"
                                font_size: "12sp"
                                theme_text_color: "Secondary"
                                adaptive_height: True
                            MDLabel:
                                id: dp_date_debut
                                text: "..."
                                adaptive_height: True
                        MDBoxLayout:
                            orientation: 'vertical'
                            adaptive_height: True
                            MDLabel:
                                text: "Date et heure fin"
                                font_size: "12sp"
                                theme_text_color: "Secondary"
                                adaptive_height: True
                            MDLabel:
                                id: dp_date_fin
                                text: "..."
                                adaptive_height: True

                    # Adresse
                    MDLabel:
                        text: "Adresse"
                        font_size: "12sp"
                        theme_text_color: "Secondary"
                        adaptive_height: True
                    MDLabel:
                        id: dp_adresse
                        text: "..."
                        adaptive_height: True

                    # Complément d'adresse
                    MDLabel:
                        text: "Complément d'adresse"
                        font_size: "12sp"
                        theme_text_color: "Secondary"
                        adaptive_height: True
                    MDLabel:
                        id: dp_complement
                        text: "..."
                        adaptive_height: True

                    # Infos supplémentaires
                    MDLabel:
                        text: "Infos supplémentaires"
                        font_size: "12sp"
                        theme_text_color: "Secondary"
                        adaptive_height: True
                    MDLabel:
                        id: dp_infos
                        text: "..."
                        adaptive_height: True

                    # Total
                    MDBoxLayout:
                        adaptive_height: True
                        spacing: "10dp"
                        padding: [0, "10dp", 0, 0]
                        MDIcon:
                            icon: "currency-eur"
                            font_size: "20sp"
                        MDLabel:
                            text: "Total"
                            font_size: "12sp"
                            theme_text_color: "Secondary"
                            adaptive_height: True
                    MDLabel:
                        id: dp_prix
                        text: "0,00€"
                        font_style: "H5"
                        bold: True
                        adaptive_height: True

            # Boutons en bas
            MDBoxLayout:
                size_hint_y: None
                height: "60dp"
                padding: "20dp", "10dp"
                spacing: "20dp"

                MDRaisedButton:
                    id: btn_refuser
                    text: "Refuser"
                    md_bg_color: 0.9, 0.9, 0.9, 1
                    text_color: 0, 0, 0, 1
                    size_hint_x: 1
                    on_release: app.refuser_prestation()

                MDRaisedButton:
                    id: btn_accepter
                    text: "Accepter"
                    md_bg_color: 0.9, 0.9, 0.9, 1
                    text_color: 0, 0, 0, 1
                    size_hint_x: 1
                    on_release: app.accepter_prestation()

    # ---------------------------------------------------
    # DÉTAILS TECHNICIEN
    # ---------------------------------------------------
    MDScreen:
        name: "detail_tech"
        MDBoxLayout:
            orientation: 'vertical'

            # Barre du haut
            MDBoxLayout:
                size_hint_y: None
                height: "56dp"
                padding: "4dp"
                MDIconButton:
                    icon: "arrow-left"
                    pos_hint: {"center_y": .5}
                    on_release: app.root.current = "main_admin"
                MDLabel:
                    text: "Détails technicien"
                    font_style: "H6"
                    bold: True
                    pos_hint: {"center_y": .5}

            MDScrollView:
                MDBoxLayout:
                    orientation: 'vertical'
                    adaptive_height: True
                    padding: "20dp"
                    spacing: "15dp"

                    # Info technicien
                    MDBoxLayout:
                        adaptive_height: True
                        spacing: "20dp"
                        MDIcon:
                            icon: "account-circle"
                            font_size: "80dp"
                        MDBoxLayout:
                            orientation: 'vertical'
                            adaptive_height: True
                            MDLabel:
                                id: dt_nom
                                text: "Nom du tech"
                                font_style: "H4"
                                bold: True
                                adaptive_height: True
                            MDLabel:
                                id: dt_email
                                text: "Email"
                                adaptive_height: True
                            MDLabel:
                                id: dt_tel
                                text: ""
                                adaptive_height: True

                    MDSeparator:
                        height: "1dp"

                    # Calendrier de disponibilités
                    MDLabel:
                        text: "Calendrier des disponibilités"
                        font_style: "H6"
                        bold: True
                        adaptive_height: True

                    MDBoxLayout:
                        id: dt_calendar_nav
                        adaptive_height: True
                        spacing: "10dp"
                        MDIconButton:
                            icon: "chevron-left"
                            on_release: app.calendrier_mois_precedent()
                        MDLabel:
                            id: dt_calendar_titre
                            text: "Mois Année"
                            halign: "center"
                            font_style: "H6"
                            adaptive_height: True
                        MDIconButton:
                            icon: "chevron-right"
                            on_release: app.calendrier_mois_suivant()

                    # Grille du calendrier (remplie dynamiquement)
                    MDGridLayout:
                        id: dt_calendar_grid
                        cols: 7
                        adaptive_height: True
                        spacing: "2dp"

                    # Légende
                    MDBoxLayout:
                        adaptive_height: True
                        spacing: "20dp"
                        padding: [0, "5dp", 0, "10dp"]
                        MDBoxLayout:
                            adaptive_height: True
                            spacing: "5dp"
                            size_hint_x: None
                            width: "120dp"
                            Widget:
                                size_hint: None, None
                                size: "14dp", "14dp"
                                canvas:
                                    Color:
                                        rgba: 0.8, 0.2, 0.2, 1
                                    Rectangle:
                                        pos: self.pos
                                        size: self.size
                            MDLabel:
                                text: "Occupé"
                                font_size: "12sp"
                                adaptive_height: True
                        MDBoxLayout:
                            adaptive_height: True
                            spacing: "5dp"
                            size_hint_x: None
                            width: "120dp"
                            Widget:
                                size_hint: None, None
                                size: "14dp", "14dp"
                                canvas:
                                    Color:
                                        rgba: 0.2, 0.7, 0.2, 1
                                    Rectangle:
                                        pos: self.pos
                                        size: self.size
                            MDLabel:
                                text: "Disponible"
                                font_size: "12sp"
                                adaptive_height: True

                    MDSeparator:
                        height: "1dp"

                    # Dernières prestations
                    MDLabel:
                        text: "Dernières prestations"
                        font_style: "H6"
                        bold: True
                        adaptive_height: True

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
            "Terminée": self.root.ids.list_terminees,
            "Annulée": self.root.ids.list_annulees
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
        self.tech_actuel_id = tech_id
        tech = Database.get_tech_details(tech_id)
        self.root.ids.dt_nom.text = f"{tech['prenom']} {tech['nom']}"
        self.root.ids.dt_email.text = tech.get('email', '')
        self.root.ids.dt_tel.text = tech.get('telephone', '') or ''

        # Charger le calendrier au mois actuel
        today = date.today()
        self.cal_annee = today.year
        self.cal_mois = today.month
        self.tech_dates_occupees = self._get_dates_occupees(tech_id)
        self._afficher_calendrier()

        # Charger l'historique des prestations
        self.root.ids.dt_list_prestas.clear_widgets()
        prestas_tech = Database.get_tech_latest_prestas(tech_id)
        if prestas_tech:
            for p in prestas_tech:
                item = TwoLineAvatarIconListItem(
                    text=f"Prestation n°{p['id_presta']} ({p['status']})",
                    secondary_text=p['adresse']
                )
                self.root.ids.dt_list_prestas.add_widget(item)
        else:
            self.root.ids.dt_list_prestas.add_widget(
                OneLineListItem(text="Aucune prestation pour le moment.")
            )

        self.root.current = "detail_tech"

    def _get_dates_occupees(self, tech_id):
        """Récupère l'ensemble des dates où le technicien est occupé"""
        prestas = Database.get_tech_prestas_with_dates(tech_id)
        dates_occupees = set()
        for p in prestas:
            debut = p.get('debut_contrat')
            fin = p.get('fin_contrat')
            if debut:
                if isinstance(debut, datetime):
                    debut = debut.date()
                elif isinstance(debut, str):
                    try:
                        debut = datetime.strptime(debut, "%Y-%m-%d").date()
                    except ValueError:
                        try:
                            debut = datetime.strptime(debut, "%Y-%m-%d %H:%M:%S").date()
                        except ValueError:
                            continue
                dates_occupees.add(debut)
                # Si on a une date de fin, marquer tous les jours entre début et fin
                if fin:
                    if isinstance(fin, datetime):
                        fin = fin.date()
                    elif isinstance(fin, str):
                        try:
                            fin = datetime.strptime(fin, "%Y-%m-%d").date()
                        except ValueError:
                            try:
                                fin = datetime.strptime(fin, "%Y-%m-%d %H:%M:%S").date()
                            except ValueError:
                                fin = None
                    if fin:
                        from datetime import timedelta
                        jour = debut
                        while jour <= fin:
                            dates_occupees.add(jour)
                            jour += timedelta(days=1)
        return dates_occupees

    def _afficher_calendrier(self):
        """Affiche la grille du calendrier pour le mois courant"""
        grid = self.root.ids.dt_calendar_grid
        grid.clear_widgets()

        # Titre du mois
        mois_noms = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
                     "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
        self.root.ids.dt_calendar_titre.text = f"{mois_noms[self.cal_mois - 1]} {self.cal_annee}"

        # En-têtes des jours
        from kivy.uix.label import Label
        from kivy.graphics import Color, Rectangle
        for jour_nom in ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]:
            lbl = Label(
                text=jour_nom, size_hint_y=None, height=30,
                font_size="12sp", color=(0.4, 0.4, 0.4, 1), bold=True
            )
            grid.add_widget(lbl)

        # Jours du mois
        cal = calendar.monthcalendar(self.cal_annee, self.cal_mois)
        for semaine in cal:
            for jour in semaine:
                if jour == 0:
                    grid.add_widget(Label(text="", size_hint_y=None, height=36))
                else:
                    d = date(self.cal_annee, self.cal_mois, jour)
                    occupe = d in self.tech_dates_occupees

                    lbl = Label(
                        text=str(jour), size_hint_y=None, height=36,
                        font_size="14sp",
                        color=(1, 1, 1, 1) if occupe else (0.1, 0.1, 0.1, 1)
                    )
                    if occupe:
                        with lbl.canvas.before:
                            Color(0.8, 0.2, 0.2, 1)
                            lbl._bg_rect = Rectangle(pos=lbl.pos, size=lbl.size)
                        lbl.bind(pos=self._update_rect, size=self._update_rect)
                    grid.add_widget(lbl)

    @staticmethod
    def _update_rect(instance, value):
        if hasattr(instance, '_bg_rect'):
            instance._bg_rect.pos = instance.pos
            instance._bg_rect.size = instance.size

    def calendrier_mois_precedent(self):
        if self.cal_mois == 1:
            self.cal_mois = 12
            self.cal_annee -= 1
        else:
            self.cal_mois -= 1
        self._afficher_calendrier()

    def calendrier_mois_suivant(self):
        if self.cal_mois == 12:
            self.cal_mois = 1
            self.cal_annee += 1
        else:
            self.cal_mois += 1
        self._afficher_calendrier()

    def aller_vers_detail_presta(self, presta_id):
        self.menu.dismiss()
        self.presta_actuelle_id = presta_id
        p = Database.get_presta_details(presta_id)

        self.root.ids.dp_titre.text = f"Prestation n°{p['id_presta']}"
        self.root.ids.dp_header.text = f"Détails prestation {p['status'].lower()}"

        # Type de prestation + status coloré
        type_presta = p.get('nom') or ""
        self.root.ids.dp_type_presta.text = type_presta
        color = "ff0000" if p['status'] == "En attente" else "00aa00" if p['status'] == "Confirmée" else "cc0000" if p['status'] == "Annulée" else "888888"
        self.root.ids.dp_status.text = f"[color=#{color}]({p['status']})[/color]"

        # Client
        client_prenom = p.get('client_prenom') or ""
        client_nom = p.get('client_nom') or ""
        self.root.ids.dp_client.text = f"{client_prenom} {client_nom}"

        # Technicien
        tech_prenom = p.get('tech_prenom')
        tech_nom = p.get('tech_nom')
        if tech_prenom and tech_nom:
            self.root.ids.dp_technicien.text = f"{tech_prenom} {tech_nom}"
        else:
            self.root.ids.dp_technicien.text = "[color=#0066cc]Assigner un technicien[/color]"

        # Type détaillé
        self.root.ids.dp_type_detail.text = type_presta if type_presta else "Non spécifié"

        # Dates
        debut = p.get('debut_contrat')
        fin = p.get('fin_contrat')
        self.root.ids.dp_date_debut.text = str(debut) if debut else "Non défini"
        self.root.ids.dp_date_fin.text = str(fin) if fin else "Non défini"

        # Adresse
        self.root.ids.dp_adresse.text = p.get('adresse') or "Non renseignée"

        # Complément d'adresse
        complement = p.get('complement_adresse') or p.get('complement') or ""
        self.root.ids.dp_complement.text = complement if complement else "-"

        # Infos supplémentaires
        infos = p.get('infos_supplementaires') or p.get('infos') or p.get('description') or ""
        self.root.ids.dp_infos.text = infos if infos else "-"

        # Prix
        prix = p.get('prix_total')
        self.root.ids.dp_prix.text = f"{prix:.2f}€".replace('.', ',') if prix else "0,00€"

        # Afficher/masquer les boutons selon le status
        show_accepter = p['status'] == "En attente"
        show_refuser = p['status'] in ["En attente", "Confirmée"]

        btn_accepter = self.root.ids.btn_accepter
        btn_accepter.opacity = 1 if show_accepter else 0
        btn_accepter.disabled = not show_accepter

        btn_refuser = self.root.ids.btn_refuser
        btn_refuser.opacity = 1 if show_refuser else 0
        btn_refuser.disabled = not show_refuser

        self.root.current = "detail_presta"

    def refuser_prestation(self):
        if self.presta_actuelle_id:
            Database.refuser_prestation(self.presta_actuelle_id)
            self.charger_apercu_rapide()
            self.root.current = "main_admin"

    def accepter_prestation(self):
        """Accepter la prestation = ouvrir l'assignation d'un technicien"""
        self.ouvrir_assignation()

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
