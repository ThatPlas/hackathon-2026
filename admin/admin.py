import sys
import os
import calendar
from datetime import datetime, date

# Ajouter le dossier parent au path pour pouvoir importer Database.py
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import Database
from utilisateur.profil import profil
from utilisateur.profil.modification import modifier_profil

from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import TwoLineAvatarIconListItem, OneLineListItem, ImageLeftWidget, IconRightWidget
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import NumericProperty

class AdminApp(MDApp):
    presta_actuelle_id = NumericProperty(None)
    utilisateur_courant = None  # Stocke les infos de l'admin connecté

    def build(self):
        self.theme_cls.primary_palette = "Gray"

        # Charger le KV du profil existant
        profil_kv_path = os.path.join(os.path.dirname(__file__), '..', 'utilisateur', 'profil', 'profil.kv')
        Builder.load_file(profil_kv_path)

        # Charger le KV de modification du profil
        modif_kv_path = os.path.join(os.path.dirname(__file__), '..', 'utilisateur', 'profil', 'modification', 'modifier_profil.kv')
        self.ecran_modif = Builder.load_file(modif_kv_path)

        # Charger l'interface admin
        kv_path = os.path.join(os.path.dirname(__file__), "admin.kv")
        root = Builder.load_file(kv_path)

        # Ajouter l'écran de modification de profil au ScreenManager
        root.add_widget(self.ecran_modif)

        # Injecter le composant ProfilContent dans l'onglet profil
        from kivy.factory import Factory
        self.vue_profil = Factory.ProfilContent()
        root.ids.profil_container.add_widget(self.vue_profil)

        return root

    def on_start(self):
        self.charger_apercu_rapide()

    # --- PROFIL (réutilise utilisateur/profil) ---
    def charger_profil(self):
        """Charge les données du profil admin via le composant ProfilContent existant"""
        if not self.utilisateur_courant:
            return
        profil.charger_donnees_profil(self.vue_profil, self.utilisateur_courant)

    def aller_vers_modifier_profil(self):
        """Navigue vers l'écran de modification du profil existant"""
        if not self.utilisateur_courant:
            return
        modifier_profil.charger_donnees(self.ecran_modif, self.utilisateur_courant)
        self.root.current = "page_modifier_profil"

    def sauvegarder_profil(self):
        """Sauvegarde les modifications du profil admin"""
        if not self.utilisateur_courant:
            return
        nom = self.ecran_modif.ids.modif_nom.text
        prenom = self.ecran_modif.ids.modif_prenom.text
        email = self.ecran_modif.ids.modif_email.text
        tel = self.ecran_modif.ids.modif_tel.text
        adr = self.ecran_modif.ids.modif_adresse.text

        Database.update_user_details(self.utilisateur_courant['id_user'], nom, prenom, email, tel, adr)
        self.utilisateur_courant = Database.get_users_details(self.utilisateur_courant['id_user'])
        self.charger_profil()
        self.root.current = "main_admin"

    def retour_profil(self):
        """Retour depuis l'écran de modification vers l'admin"""
        self.root.current = "main_admin"

    def deconnexion(self):
        """Déconnexion de l'admin"""
        self.utilisateur_courant = None
        self.stop()

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
        for tech in Database.get_all_technicians():
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
        techs = Database.get_all_technicians()
        
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
