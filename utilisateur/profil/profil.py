def charger_donnees_profil(widget_profil, data):
    """
    widget_profil est le composant 'vue_profil' envoyé par login.py
    data contient les infos de la BDD (nom, prenom, email, mdp, etc.)
    """
    # Mise à jour du nom et prénom
    widget_profil.ids.label_nom_titre.text = f"{data['nom']} {data['prenom']}"
    
    # Mise à jour du téléphone
    tel = data.get('telephone')
    widget_profil.ids.item_tel.secondary_text = str(tel) if tel else "Non renseigné"
    
    # Mise à jour de l'adresse
    adr = data.get('adresse')
    widget_profil.ids.item_adresse.secondary_text = str(adr) if adr else "Non renseignée"