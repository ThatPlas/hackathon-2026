def charger_donnees(screen, data):
    """Pré-remplit les champs avec les données actuelles"""
    screen.ids.modif_nom.text = data.get('nom', '')
    screen.ids.modif_prenom.text = data.get('prenom', '')
    screen.ids.modif_email.text = data.get('email', '')
    
    tel = data.get('telephone')
    screen.ids.modif_tel.text = str(tel) if tel else ""
    
    adr = data.get('adresse')
    screen.ids.modif_adresse.text = str(adr) if adr else ""