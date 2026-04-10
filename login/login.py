from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivymd.uix.list import OneLineListItem, ThreeLineAvatarIconListItem, IconLeftWidget, IconRightWidget, TwoLineAvatarIconListItem, ImageLeftWidget
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.label import MDLabel
from kivy.metrics import dp
from kivymd.uix.card import MDCard
from kivy.animation import Animation
from datetime import datetime, date
import calendar
import sys
import os

# --- CORRECTION DES CHEMINS ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from notif.notif import NotifScreen
from utilisateur.profil import profil
from utilisateur.profil.modification import modifier_profil
import Database


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
    utilisateur_courant = None
    current_service_id = NumericProperty(0)
    presta_actuelle_id = NumericProperty(None)

    # Référence au ScreenManager interne de l'admin (fix principal)
    sm_admin = None

    def build(self):
        self.theme_cls.primary_palette = "Red"

        # 1. Charger le KV des notifications
        try:
            chemin_notif_kv = os.path.join(ROOT_DIR, 'notif', 'notif.kv')
            Builder.load_file(chemin_notif_kv)
        except Exception as e:
            print(f"Note : notif.kv non chargé : {e}")

        # 2. Charger le ScreenManager principal (login.kv)
        sm = Builder.load_file("login.kv")

        # --- Écran inscription ---
        chemin_insc = os.path.join(ROOT_DIR, 'inscription', 'inscription.kv')
        sm.add_widget(Builder.load_file(chemin_insc))

        # --- Écran client ---
        chemin_accueil = os.path.join(ROOT_DIR, 'utilisateur', 'Accueil', 'Accueil.kv')
        self.ecran_client = Builder.load_file(chemin_accueil)
        sm.add_widget(self.ecran_client)

        # --- Écran modification profil ---
        chemin_modif = os.path.join(ROOT_DIR, 'utilisateur', 'profil', 'modification', 'modifier_profil.kv')
        self.ecran_modif = Builder.load_file(chemin_modif)
        sm.add_widget(self.ecran_modif)

        # --- Écran contact ---
        chemin_contact = os.path.join(ROOT_DIR, 'contact.kv')
        self.ecran_contact = Builder.load_file(chemin_contact)
        sm.add_widget(self.ecran_contact)

        # --- Écran admin ---
        # FIX : on garde une référence au ScreenManager interne de l'admin (sm_admin)
        # pour que toutes les méthodes admin utilisent sm_admin.ids au lieu de self.root.ids
        try:
            from kivymd.uix.screen import MDScreen
            from kivy.factory import Factory

            chemin_admin = os.path.join(ROOT_DIR, 'admin', 'admin.kv')
            contenu_admin = Builder.load_file(chemin_admin)

            # sm_admin = le ScreenManager interne de l'admin (contient main_admin, detail_presta, etc.)
            self.sm_admin = contenu_admin

            # On enveloppe dans un MDScreen pour le ScreenManager principal
            self.ecran_admin = MDScreen(name="espace_admin")
            self.ecran_admin.add_widget(contenu_admin)
            sm.add_widget(self.ecran_admin)

            # FIX : injection du ProfilContent dans l'onglet profil admin (manquait depuis login.py)
            self.vue_profil_admin = Factory.ProfilContent()
            contenu_admin.ids.profil_container.add_widget(self.vue_profil_admin)

        except Exception as e:
            print(f"Erreur chargement admin : {e}")

        # --- Écran technicien ---
        try:
            from kivymd.uix.screen import MDScreen
            chemin_tech = os.path.join(ROOT_DIR, 'tech', 'interface_design.kv')
            self.ecran_tech = Builder.load_file(chemin_tech)
            ecran_conteneur = MDScreen(name="espace_technicien")
            ecran_conteneur.add_widget(self.ecran_tech)
            sm.add_widget(ecran_conteneur)
            print("SUCCÈS : Écran technicien chargé et ajouté !")
        except Exception as e:
            print(f"ERREUR au chargement du technicien : {e}")

        # --- Injection de l'écran de notification dans le client ---
        try:
            recherche_sm = self.ecran_client.ids.contenu_recherche.ids.search_screen_manager
            recherche_sm.add_widget(NotifScreen(name='page_notif'))
        except Exception as e:
            print(f"Erreur injection NotifScreen : {e}")

        return sm

    # ==========================================
    # NAVIGATION PRINCIPALE
    # ==========================================
    def aller_a_inscription(self):
        self.root.current = "page_inscription"

    def aller_a_connexion(self):
        self.root.current = "page_connexion"

    def deconnexion(self):
        self.utilisateur_courant = None
        self.root.current = "page_connexion"
        self.root.ids.champ_email.text = ""
        self.root.ids.champ_mdp.text = ""

    def retour_profil(self):
        self.root.current = "espace_client"

    def aller_vers_modifier_profil(self):
        if self.utilisateur_courant:
            self.root.current = "page_modifier_profil"
            modifier_profil.charger_donnees(self.ecran_modif, self.utilisateur_courant)

    def aller_vers_contact(self):
        self.root.current = "page_contact"

    # ==========================================
    # CONNEXION / INSCRIPTION
    # ==========================================
    def tenter_connexion(self, email_saisi, mdp_saisi):
        self.root.ids.message_erreur.text = ""
        if not email_saisi or not mdp_saisi:
            self.root.ids.message_erreur.text = "Veuillez remplir tous les champs."
            return

        try:
            utilisateur = Database.authenticate_users(email_saisi, mdp_saisi)
            if not utilisateur:
                self.root.ids.message_erreur.text = "Email ou mot de passe incorrect."
                return

            role = Database.get_user_role(utilisateur['id_user'])
            self.utilisateur_courant = utilisateur

            if role == "client":
                self.root.current = "espace_client"
                profil.charger_donnees_profil(self.ecran_client.ids.contenu_profil, utilisateur)
                self.filter_services("")

            elif role == "admin":
                self.root.current = "espace_admin"
                self.charger_apercu_rapide()

            elif role == "technicien":
                self.root.current = "espace_technicien"
                self.ecran_tech.ids.screen_manager.current = "main_screen"
                self.ecran_tech.ids.profil_nom.text = f"{utilisateur['prenom']} {utilisateur['nom']}"
                self.ecran_tech.ids.profil_email.text = utilisateur['email']
                self.charger_donnees_technicien()

            else:
                self.root.current = "page_connexion"

        except Exception as e:
            print(f"Erreur connexion : {e}")
            self.root.ids.message_erreur.text = "Erreur serveur."

    # ==========================================
    # LOGIQUE RECHERCHE, PANIER ET NOTIF (CLIENT)
    # ==========================================
    def ouvrir_notif(self):
        try:
            self.ecran_client.ids.nav_bar.switch_tab('page_recherche')
            recherche_ui = self.ecran_client.ids.contenu_recherche.ids
            recherche_ui.search_screen_manager.transition.direction = "left"
            recherche_ui.search_screen_manager.current = 'page_notif'
        except Exception as e:
            print(f"Erreur navigation notif : {e}")

    def retour_recherche(self):
        recherche_ui = self.ecran_client.ids.contenu_recherche.ids
        recherche_ui.search_screen_manager.transition.direction = "right"
        recherche_ui.search_screen_manager.current = 'liste_recherche'

    def filter_services(self, query=""):
        try:
            recherche_ui = self.ecran_client.ids.contenu_recherche.ids
            container = recherche_ui.container_prestations
            container.clear_widgets()
            query = query.lower().strip()
            all_categories = Database.get_categories()

            for category in all_categories:
                cat_name_display = category["nom"].strip()
                cat_name_lower = cat_name_display.lower()
                all_types = Database.get_type_prestas_by_category(category['id_categorie'])
                matching_types = [t for t in all_types if query in t["nom"].lower()]

                if query == "" or query in cat_name_lower or matching_types:
                    img_path = os.path.join(ROOT_DIR, 'images', f"{cat_name_lower}.jpg")
                    card = ServiceCard(image_source=img_path, title_text=cat_name_display)
                    list_to_show = all_types if (query == "" or query in cat_name_lower) else matching_types
                    for p in list_to_show:
                        item = OneLineListItem(
                            text=f"{p['nom']} - {p['prix']}€",
                            divider="Full",
                            on_release=lambda x, data=p: self.ouvrir_details(data)
                        )
                        card.ids.sub_services_list.add_widget(item)
                    container.add_widget(card)
        except Exception as e:
            print(f"Attente d'initialisation : {e}")

    def ouvrir_details(self, data):
        recherche_ui = self.ecran_client.ids.contenu_recherche.ids
        self.current_service_id = data['id_type_presta']
        recherche_ui.detail_titre.text = data['nom']
        recherche_ui.detail_desc.text = data['description']
        recherche_ui.detail_prix.text = f"Prix : {data['prix']} €"
        recherche_ui.input_date.text = datetime.now().strftime("%d/%m/%Y")
        recherche_ui.input_hour.text = ""
        recherche_ui.search_screen_manager.transition.direction = "left"
        recherche_ui.search_screen_manager.current = 'details_presta'

    def ouvrir_panier(self):
        self.charger_panier()
        recherche_ui = self.ecran_client.ids.contenu_recherche.ids
        recherche_ui.search_screen_manager.transition.direction = "left"
        recherche_ui.search_screen_manager.current = 'page_panier'

    def charger_panier(self):
        recherche_ui = self.ecran_client.ids.contenu_recherche.ids
        panier_list = recherche_ui.panier_list
        panier_list.clear_widgets()
        user_id = self.utilisateur_courant['id_user'] if self.utilisateur_courant else 1
        items = Database.get_user_panier(user_id)
        total = 0
        for item in items:
            total += float(item['prix'])
            dt = item['debut_contrat']
            date_formatee = dt.strftime("%d/%m/%Y à %Hh%M") if isinstance(dt, datetime) else str(dt)
            row = ThreeLineAvatarIconListItem(
                text=item['nom'],
                secondary_text=f"Prix : {item['prix']}€",
                tertiary_text=f"{date_formatee}"
            )
            row.add_widget(IconLeftWidget(icon="tag-outline"))
            delete_btn = IconRightWidget(
                icon="trash-can-outline",
                theme_text_color="Error",
                on_release=lambda x, id_p=item['id_presta']: self.supprimer_du_panier(id_p)
            )
            row.add_widget(delete_btn)
            panier_list.add_widget(row)
        recherche_ui.total_label.text = f"{total:.2f} €"

    def supprimer_du_panier(self, id_presta):
        try:
            Database.delete_prestation(id_presta)
            self.charger_panier()
            self.afficher_message("Prestation supprimée", couleur=[1, 0, 0, 1])
        except Exception as e:
            self.afficher_message(f"Erreur : {e}")

    def ajouter_prestation(self):
        recherche_ui = self.ecran_client.ids.contenu_recherche.ids
        date_txt = recherche_ui.input_date.text.strip()
        heure_txt = recherche_ui.input_hour.text.strip()
        if not date_txt or not heure_txt:
            self.afficher_message("Remplissez la date et l'heure !")
            return
        try:
            debut = datetime.strptime(f"{date_txt} {heure_txt}", "%d/%m/%Y %H:%M")
            fin = debut
            user_id = self.utilisateur_courant['id_user'] if self.utilisateur_courant else 1
            adresse = self.utilisateur_courant.get('adresse', '') if self.utilisateur_courant else ''
            Database.create_prestation(user_id, self.current_service_id, debut, fin, adresse)
            self.afficher_message("Ajouté au panier !", couleur=[0, 0.6, 0, 1])
            recherche_ui.search_screen_manager.transition.direction = "right"
            recherche_ui.search_screen_manager.current = 'liste_recherche'
        except ValueError:
            self.afficher_message("Format Date ou Heure invalide !", couleur=[1, 0, 0, 1])
        except Exception as e:
            self.afficher_message(f"Erreur : {str(e)}")

    def payer_commande(self):
        try:
            user_id = self.utilisateur_courant['id_user'] if self.utilisateur_courant else 1
            Database.valider_panier_db(user_id)
            self.charger_panier()
            self.afficher_message("Réservation en attente de validation", couleur=[0, 0.6, 0, 1])
            recherche_ui = self.ecran_client.ids.contenu_recherche.ids
            recherche_ui.search_screen_manager.transition.direction = "right"
            recherche_ui.search_screen_manager.current = 'liste_recherche'
        except Exception as e:
            self.afficher_message(f"Erreur lors du paiement : {e}")

    def afficher_message(self, texte, couleur=[0.4, 0.1, 0.2, 1]):
        try:
            snackbar = Snackbar(bg_color=couleur)
            label = MDLabel(text=texte, theme_text_color="Custom", text_color=[1, 1, 1, 1], valign="center")
            snackbar.add_widget(label)
            snackbar.open()
        except:
            print(f"Notification : {texte}")

    # ==========================================
    # LOGIQUE PROFIL & CONTACT (CLIENT)
    # ==========================================
    def sauvegarder_profil(self):
        nom = self.ecran_modif.ids.modif_nom.text
        prenom = self.ecran_modif.ids.modif_prenom.text
        email = self.ecran_modif.ids.modif_email.text
        tel = self.ecran_modif.ids.modif_tel.text
        adr = self.ecran_modif.ids.modif_adresse.text

        Database.update_user_details(self.utilisateur_courant['id_user'], nom, prenom, email, tel, adr)
        self.utilisateur_courant = Database.get_users_details(self.utilisateur_courant['id_user'])
        widget_p = self.ecran_client.ids.contenu_profil
        profil.charger_donnees_profil(widget_p, self.utilisateur_courant)
        self.retour_profil()

    def envoyer_contact(self, nom, prenom, adresse, ville, email, telephone, message):
        if not nom or not prenom or not email or not message:
            print("Erreur : Les champs obligatoires ne sont pas remplis.")
            return
        print(f"Demande reçue de {nom} {prenom} ({email}) : {message}")
        self.ecran_contact.ids.contact_message.text = ""
        self.retour_profil()

    # ==========================================
    # LOGIQUE ADMIN
    # FIX : toutes les méthodes utilisent self.sm_admin.ids
    #       au lieu de self.root.ids
    # ==========================================

    def naviguer_admin(self, screen_name):
        """Navigation interne à l'espace admin (appelée depuis admin.kv)"""
        if self.sm_admin:
            self.sm_admin.current = screen_name

    def charger_apercu_rapide(self):
        if not self.sm_admin:
            return
        sm = self.sm_admin  # FIX : sm_admin au lieu de self.root

        sm.ids.list_last_techs.clear_widgets()
        for tech in Database.get_last_5_techs():
            item = self.creer_list_item(
                f"{tech['prenom']} {tech['nom']}", "Technicien",
                lambda inst, tid=tech['id_user']: self.ouvrir_menu_tech(inst, tid)
            )
            sm.ids.list_last_techs.add_widget(item)

        status_mapping = {
            "En attente": sm.ids.list_attente,
            "Confirmée":  sm.ids.list_confirmees,
            "Terminée":   sm.ids.list_terminees,
            "Annulée":    sm.ids.list_annulees
        }
        for status, widget in status_mapping.items():
            widget.clear_widgets()
            for p in Database.get_last_5_prestas_by_status(status):
                item = self.creer_list_item(
                    f"Prestation n°{p['id_presta']}", p['adresse'],
                    lambda inst, pid=p['id_presta']: self.ouvrir_menu_presta(inst, pid)
                )
                widget.add_widget(item)

    def charger_tous_les_techniciens(self):
        if not self.sm_admin:
            return
        self.sm_admin.ids.list_all_techs.clear_widgets()
        for tech in Database.get_all_technicians():
            item = self.creer_list_item(
                f"{tech['prenom']} {tech['nom']}", "Technicien",
                lambda inst, tid=tech['id_user']: self.ouvrir_menu_tech(inst, tid)
            )
            self.sm_admin.ids.list_all_techs.add_widget(item)

    def creer_list_item(self, titre, sous_titre, action_menu):
        item = TwoLineAvatarIconListItem(text=titre, secondary_text=sous_titre, bg_color=(1, 1, 1, 1))
        item.add_widget(ImageLeftWidget(source=""))
        btn = IconRightWidget(icon="dots-vertical")
        btn.bind(on_release=lambda x, inst=btn: action_menu(inst))
        item.add_widget(btn)
        return item

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

    def aller_vers_detail_tech(self, tech_id):
        self.menu.dismiss()
        self.tech_actuel_id = tech_id
        tech = Database.get_tech_details(tech_id)
        sm = self.sm_admin  # FIX
        sm.ids.dt_nom.text = f"{tech['prenom']} {tech['nom']}"
        sm.ids.dt_email.text = tech.get('email', '')
        sm.ids.dt_tel.text = tech.get('telephone', '') or ''

        today = date.today()
        self.cal_annee = today.year
        self.cal_mois = today.month
        self.tech_dates_occupees = self._get_dates_occupees(tech_id)
        self._afficher_calendrier()

        sm.ids.dt_list_prestas.clear_widgets()
        prestas_tech = Database.get_tech_latest_prestas(tech_id)
        if prestas_tech:
            for p in prestas_tech:
                item = TwoLineAvatarIconListItem(
                    text=f"Prestation n°{p['id_presta']} ({p['status']})",
                    secondary_text=p['adresse']
                )
                sm.ids.dt_list_prestas.add_widget(item)
        else:
            sm.ids.dt_list_prestas.add_widget(OneLineListItem(text="Aucune prestation pour le moment."))

        sm.current = "detail_tech"  # FIX

    def aller_vers_detail_presta(self, presta_id):
        self.menu.dismiss()
        self.presta_actuelle_id = presta_id
        p = Database.get_presta_details(presta_id)
        sm = self.sm_admin  # FIX

        sm.ids.dp_titre.text = f"Prestation n°{p['id_presta']}"
        sm.ids.dp_header.text = f"Détails prestation {p['status'].lower()}"

        type_presta = p.get('nom') or ""
        sm.ids.dp_type_presta.text = type_presta
        color_map = {"En attente": "ff0000", "Confirmée": "00aa00", "Terminée": "0000ff", "Annulée": "888888"}
        color = color_map.get(p['status'], "000000")
        sm.ids.dp_status.text = f"[color=#{color}]{p['status']}[/color]"

        sm.ids.dp_client.text = p.get('client', '')
        sm.ids.dp_adresse.text = p.get('adresse', '')
        sm.ids.dp_date.text = str(p.get('debut_contrat', ''))
        prix = str(p.get('prix', '')).replace('.', ',') if p.get('prix') else "0,00€"
        sm.ids.dp_prix.text = prix

        show_accepter = p['status'] == "En attente"
        show_refuser = p['status'] in ["En attente", "Confirmée"]

        btn_accepter = sm.ids.btn_accepter
        btn_accepter.opacity = 1 if show_accepter else 0
        btn_accepter.disabled = not show_accepter

        btn_refuser = sm.ids.btn_refuser
        btn_refuser.opacity = 1 if show_refuser else 0
        btn_refuser.disabled = not show_refuser

        sm.current = "detail_presta"  # FIX

    def refuser_prestation(self):
        if self.presta_actuelle_id:
            Database.refuser_prestation(self.presta_actuelle_id)
            self.charger_apercu_rapide()
            self.sm_admin.current = "main_admin"  # FIX

    def accepter_prestation(self):
        self.ouvrir_assignation()

    def sauvegarder_technicien(self):
        sm = self.sm_admin  # FIX
        nom    = sm.ids.input_nom.text
        prenom = sm.ids.input_prenom.text
        email  = sm.ids.input_email.text
        tel    = sm.ids.input_tel.text
        mdp    = sm.ids.input_mdp.text

        if nom and prenom and email:
            succes = Database.add_technicien(nom, prenom, email, tel, mdp)
            if succes:
                sm.ids.input_nom.text = ""
                sm.ids.input_prenom.text = ""
                sm.ids.input_email.text = ""
                sm.ids.input_tel.text = ""
                sm.ids.input_mdp.text = ""
                self.charger_tous_les_techniciens()
                self.charger_apercu_rapide()
                sm.current = "main_admin"  # FIX

    def ouvrir_assignation(self):
        sm = self.sm_admin  # FIX
        sm.ids.list_techs_dispo.clear_widgets()
        techs = Database.get_all_technicians()
        for tech in techs:
            item = TwoLineAvatarIconListItem(
                text=f"{tech['prenom']} {tech['nom']}",
                secondary_text="Cliquer pour assigner"
            )
            item.bind(on_release=lambda x, tid=tech['id_user']: self.confirmer_assignation(tid))
            sm.ids.list_techs_dispo.add_widget(item)
        sm.current = "assigner_tech"  # FIX

    def confirmer_assignation(self, tech_id):
        if self.presta_actuelle_id:
            Database.assign_tech_to_presta(self.presta_actuelle_id, tech_id)
            self.charger_apercu_rapide()
            self.aller_vers_detail_presta(self.presta_actuelle_id)

    def charger_profil_admin(self):
        if self.utilisateur_courant and hasattr(self, 'vue_profil_admin'):
            profil.charger_donnees_profil(self.vue_profil_admin, self.utilisateur_courant)

    def aller_vers_modifier_profil_admin(self):
        if self.utilisateur_courant:
            modifier_profil.charger_donnees(self.ecran_modif, self.utilisateur_courant)
            self.root.current = "page_modifier_profil"

    def sauvegarder_profil_admin(self):
        if not self.utilisateur_courant:
            return
        nom    = self.ecran_modif.ids.modif_nom.text
        prenom = self.ecran_modif.ids.modif_prenom.text
        email  = self.ecran_modif.ids.modif_email.text
        tel    = self.ecran_modif.ids.modif_tel.text
        adr    = self.ecran_modif.ids.modif_adresse.text
        Database.update_user_details(self.utilisateur_courant['id_user'], nom, prenom, email, tel, adr)
        self.utilisateur_courant = Database.get_users_details(self.utilisateur_courant['id_user'])
        self.charger_profil_admin()
        self.sm_admin.current = "main_admin"

    # --- Calendrier technicien ---
    def _get_dates_occupees(self, tech_id):
        try:
            prestas = Database.get_tech_latest_prestas(tech_id)
            dates = set()
            for p in prestas:
                if p.get('debut_contrat'):
                    dates.add(p['debut_contrat'].date() if hasattr(p['debut_contrat'], 'date') else p['debut_contrat'])
            return dates
        except:
            return set()

    def _afficher_calendrier(self):
        try:
            from kivy.uix.label import Label
            from kivy.graphics import Color, Rectangle
            sm = self.sm_admin
            grid = sm.ids.cal_grid
            grid.clear_widgets()
            sm.ids.cal_label.text = f"{calendar.month_name[self.cal_mois]} {self.cal_annee}"
            for jour_nom in ["L", "M", "M", "J", "V", "S", "D"]:
                grid.add_widget(Label(text=jour_nom, bold=True, color=(0, 0, 0, 1)))
            cal = calendar.monthcalendar(self.cal_annee, self.cal_mois)
            for semaine in cal:
                for jour in semaine:
                    if jour == 0:
                        grid.add_widget(Label(text=""))
                    else:
                        d = date(self.cal_annee, self.cal_mois, jour)
                        occupe = d in self.tech_dates_occupees
                        lbl = Label(
                            text=str(jour),
                            color=(1, 1, 1, 1) if occupe else (0.1, 0.1, 0.1, 1)
                        )
                        if occupe:
                            with lbl.canvas.before:
                                Color(0.8, 0.2, 0.2, 1)
                                lbl._bg_rect = Rectangle(pos=lbl.pos, size=lbl.size)
                            lbl.bind(pos=self._update_rect, size=self._update_rect)
                        grid.add_widget(lbl)
        except Exception as e:
            print(f"Erreur calendrier : {e}")

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

    # ==========================================
    # LOGIQUE TECHNICIEN
    # ==========================================
    def charger_donnees_technicien(self):
        for container_id, p_type in [("container_prestations", "historique"),
                                     ("container_en_cours", "en_cours"),
                                     ("upcoming_container", "a_venir")]:
            container = self.ecran_tech.ids[container_id]
            container.clear_widgets()
            for item in self.get_mock_data_tech(p_type):
                container.add_widget(self.create_prestation_item_tech(item))

    def get_mock_data_tech(self, p_type):
        data = {
            "historique": [{"titre": "Audit sécurité", "info": "10/03/2026", "type": "historique"}],
            "en_cours":   [{"titre": "Entretien espaces verts", "info": "Aujourd'hui", "type": "en_cours"}],
            "a_venir":    [{"titre": "Audit IT", "info": "20/04/2026", "type": "a_venir"}]
        }
        return data.get(p_type, [])

    def create_prestation_item_tech(self, data):
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.button import MDIconButton
        card = MDCard(orientation="horizontal", size_hint=(1, None), height=dp(65), radius=[12], elevation=2, padding=dp(8))
        text_layout = MDBoxLayout(orientation="vertical")
        text_layout.add_widget(MDLabel(text=data["titre"], font_style="Body1", bold=True))
        text_layout.add_widget(MDLabel(text=data["info"], font_style="Caption", theme_text_color="Secondary"))
        btn = MDIconButton(icon="dots-vertical")
        btn.bind(on_release=lambda x: self.ouvrir_detail_tech(data))
        card.add_widget(text_layout)
        card.add_widget(btn)
        return card

    def ouvrir_detail_tech(self, data):
        p_type = data.get("type", "historique")
        ids = self.ecran_tech.ids
        prefix = "hi_" if p_type == "historique" else "ec_" if p_type == "en_cours" else "av_"
        target = f"detail_{p_type}"
        ids[f"{prefix}subtitle"].text = data["titre"]
        ids[f"{prefix}adresse"].text = "13 rue du test, Lille"
        ids.screen_manager.current = target

    def aller_vers_detail_presta(self, presta_id):
        self.menu.dismiss()
        self.presta_actuelle_id = presta_id
        p = Database.get_presta_details(presta_id)
        sm = self.sm_admin

        sm.ids.dp_titre.text = f"Prestation n°{p['id_presta']}"
        sm.ids.dp_header.text = f"Détails prestation {p['status'].lower()}"

        type_presta = p.get('nom') or ""
        sm.ids.dp_type_presta.text = type_presta
        color_map = {"En attente": "ff0000", "Confirmée": "00aa00", "Terminée": "0000ff", "Annulée": "888888"}
        color = color_map.get(p['status'], "000000")
        sm.ids.dp_status.text = f"[color=#{color}]{p['status']}[/color]"

        # --- CORRECTION DES IDs ICI ---
        # Client
        client_prenom = p.get('client_prenom') or ""
        client_nom = p.get('client_nom') or p.get('client') or ""
        sm.ids.dp_client.text = f"{client_prenom} {client_nom}".strip()

        # Technicien
        tech_prenom = p.get('tech_prenom')
        tech_nom = p.get('tech_nom')
        if tech_prenom and tech_nom:
            sm.ids.dp_technicien.text = f"{tech_prenom} {tech_nom}"
        else:
            sm.ids.dp_technicien.text = "[color=#0066cc]Assigner un technicien[/color]"

        # Détails supplémentaires
        sm.ids.dp_type_detail.text = type_presta if type_presta else "Non spécifié"
        
        # Remplacement de dp_date par dp_date_debut et dp_date_fin
        debut = p.get('debut_contrat')
        fin = p.get('fin_contrat')
        sm.ids.dp_date_debut.text = str(debut) if debut else "Non défini"
        sm.ids.dp_date_fin.text = str(fin) if fin else "Non défini"
        
        sm.ids.dp_adresse.text = p.get('adresse') or "Non renseignée"
        
        complement = p.get('complement_adresse') or p.get('complement') or ""
        sm.ids.dp_complement.text = complement if complement else "-"

        infos = p.get('infos_supplementaires') or p.get('infos') or p.get('description') or ""
        sm.ids.dp_infos.text = infos if infos else "-"
        # -------------------------------

        prix = str(p.get('prix_total') or p.get('prix') or '').replace('.', ',')
        sm.ids.dp_prix.text = f"{prix}€" if prix else "0,00€"

        show_accepter = p['status'] == "En attente"
        show_refuser = p['status'] in ["En attente", "Confirmée"]

        btn_accepter = sm.ids.btn_accepter
        btn_accepter.opacity = 1 if show_accepter else 0
        btn_accepter.disabled = not show_accepter

        btn_refuser = sm.ids.btn_refuser
        btn_refuser.opacity = 1 if show_refuser else 0
        btn_refuser.disabled = not show_refuser

        sm.current = "detail_presta"


if __name__ == "__main__":
    ConciergerieApp().run()