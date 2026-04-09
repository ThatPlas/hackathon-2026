import mysql.connector
from datetime import datetime, timedelta

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="conciergerie_desruelle"
    )

def get_categories():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM categorie")
    categories = cursor.fetchall()
    cursor.close()
    conn.close()
    return categories

def get_type_prestas_by_category(category_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM type_presta WHERE id_categorie = %s", (category_id,))
    type_prestas = cursor.fetchall()
    cursor.close()
    conn.close()
    return type_prestas

def get_type_presta_details(presta_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM type_presta WHERE id_type_presta = %s", (presta_id,))
    type_presta = cursor.fetchone()
    cursor.close()
    conn.close()
    return type_presta

def user_exists(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_user FROM user WHERE email = %s", (email,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result is not None

def create_users(nom, prenom, email, mdp):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # 1. On crée l'utilisateur
        cursor.execute("INSERT INTO user (nom, prenom, email, mdp) VALUES (%s, %s, %s, %s)",
                       (nom, prenom, email, mdp))
        
        # 2. On récupère l'ID généré par la base de données
        nouvel_id = cursor.lastrowid
        
        # 3. On déclare automatiquement cette personne comme Client
        cursor.execute("INSERT INTO client (id_user) VALUES (%s)", (nouvel_id,))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Erreur lors de la création : {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def authenticate_users(email, mdp):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user WHERE email = %s AND mdp = %s", (email, mdp))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def get_users_details(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user WHERE id_user = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def update_user_details(user_id, nom, prenom, email, telephone, adresse):
    """Met à jour toutes les informations de l'utilisateur (incluant tel et adresse)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE user 
        SET nom = %s, prenom = %s, email = %s, telephone = %s, adresse = %s 
        WHERE id_user = %s
    """, (nom, prenom, email, telephone, adresse, user_id))
    conn.commit()
    cursor.close()
    conn.close()

# --- Fonctions pour les Prestations et le Panier ---

def create_prestation(id_user, id_type_presta, debut, fin, adresse):
    conn = get_connection()
    cursor = conn.cursor()
    # On initialise le statut à 'dans_panier'
    cursor.execute("INSERT INTO prestation (id_user, debut_contrat, fin_contrat, adresse, status) VALUES (%s, %s, %s, %s, %s)",
                   (id_user, debut, fin, adresse, "dans_panier"))
    id_presta = cursor.lastrowid
    cursor.execute("INSERT INTO relation_type_presta (id_presta, id_type_presta) VALUES (%s, %s)",
                   (id_presta, id_type_presta))
    conn.commit()
    cursor.close()
    conn.close()

def get_user_panier(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT tp.nom, tp.prix, p.id_presta 
        FROM prestation p
        JOIN relation_type_presta rtp ON p.id_presta = rtp.id_presta
        JOIN type_presta tp ON rtp.id_type_presta = tp.id_type_presta
        WHERE p.id_user = %s AND p.status = 'dans_panier'
    """
    cursor.execute(query, (user_id,))
    res = cursor.fetchall()
    cursor.close()
    conn.close()
    return res

def valider_panier_db(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    query = "UPDATE prestation SET status = 'En attente' WHERE id_user = %s AND status = 'dans_panier'"
    cursor.execute(query, (user_id,))
    conn.commit()
    cursor.close()
    conn.close()

def get_notifs(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM notif WHERE id_user = %s", (user_id,))
    notifs = cursor.fetchall()
    cursor.close()
    conn.close()
    return notifs

def mark_notif_as_read(notif_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE notif SET a_lu = 1 WHERE id_notif = %s", (notif_id,))
    conn.commit()
    cursor.close()
    conn.close()

def get_prestations_by_user(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.*, GROUP_CONCAT(tp.nom_type_presta) AS types_presta
        FROM presta p
        JOIN relation_type_presta rtp ON p.id_presta = rtp.id_presta
        JOIN type_presta tp ON rtp.id_type_presta = tp.id_type_presta
        WHERE p.id_user = %s
        GROUP BY p.id_presta
    """, (user_id,))
    prestations = cursor.fetchall()
    cursor.close()
    conn.close()
    return prestations

def get_user_history(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.id_presta, p.status, p.debut_contrat, p.prix_total, tp.nom 
        FROM prestation p
        JOIN relation_type_presta rtp ON p.id_presta = rtp.id_presta
        JOIN type_presta tp ON rtp.id_type_presta = tp.id_type_presta
        WHERE p.id_user = %s
        ORDER BY p.debut_contrat DESC
    """, (user_id,))
    history = cursor.fetchall()
    cursor.close()
    conn.close()
    return history

def cancel_prestation(presta_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT debut_contrat FROM prestation WHERE id_presta = %s", (presta_id,))
    presta = cursor.fetchone()
    
    if not presta:
        cursor.close()
        conn.close()
        return "Prestation introuvable"

    maintenant = datetime.now()
    debut = presta['debut_contrat']
    
    peut_etre_rembourse = (debut - maintenant) > timedelta(hours=24)

    nouveau_statut = "Annulée - Remboursée" if peut_etre_rembourse else "Annulée - Non remboursée"
    
    cursor.execute("UPDATE prestation SET status = %s WHERE id_presta = %s", 
                   (nouveau_statut, presta_id))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return nouveau_statut

def assign_technician_to_prestation(id_presta, id_tech):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO disponibilite (id_user, id_presta) VALUES (%s, %s)", 
                       (id_tech, id_presta))
        
        cursor.execute("UPDATE prestation SET status = 'confirmée' WHERE id_presta = %s", 
                       (id_presta,))
        
        cursor.execute("INSERT INTO notif (message, id_prestation, a_lu) VALUES (%s, %s, %s)",
                       (f"Nouvelle mission assignée : #{id_presta}", id_presta, 'Non'))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Erreur d'assignation : {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def get_unassigned_prestations():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.*, u.nom as client_nom, u.prenom as client_prenom
        FROM prestation p
        JOIN user u ON p.id_user = u.id_user
        LEFT JOIN disponibilite d ON p.id_presta = d.id_presta
        WHERE d.id_user IS NULL AND p.status = 'en attente'
    """)
    unassigned = cursor.fetchall()
    cursor.close()
    conn.close()
    return unassigned

def get_all_technicians():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.id_user, u.nom, u.prenom, u.email 
        FROM user u
        JOIN technicien t ON u.id_user = t.id_user
    """)
    techs = cursor.fetchall()
    cursor.close()
    conn.close()
    return techs

def get_user_role(user_id):
    """Cherche dans les tables enfants pour déterminer le rôle de l'utilisateur"""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Test 1 : Admin ?
        cursor.execute("SELECT id_user FROM admin WHERE id_user = %s", (user_id,))
        if cursor.fetchone(): return "admin"

        # Test 2 : Technicien ?
        cursor.execute("SELECT id_user FROM technicien WHERE id_user = %s", (user_id,))
        if cursor.fetchone(): return "technicien"

        # Test 3 : Client ?
        cursor.execute("SELECT id_user FROM client WHERE id_user = %s", (user_id,))
        if cursor.fetchone(): return "client"

        # Si trouvé nulle part
        return None
        
    finally:
        cursor.close()
        conn.close()