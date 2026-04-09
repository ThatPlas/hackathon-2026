import mysql.connector

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
        # 1. On crée l'utilisateur (Votre code d'origine)
        cursor.execute("INSERT INTO user (nom, prenom, email, mdp) VALUES (%s, %s, %s, %s)",
                       (nom, prenom, email, mdp))
        
        # 2. LA NOUVEAUTÉ : On récupère l'ID généré par la base de données
        nouvel_id = cursor.lastrowid
        
        # 3. LA NOUVEAUTÉ : On déclare automatiquement cette personne comme Client
        cursor.execute("INSERT INTO client (id_user) VALUES (%s)", (nouvel_id,))
        
        conn.commit()
        return True # On renvoie True pour dire à l'écran Kivy que c'est un succès
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

def update_user_details(user_id, nom, prenom, email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE user SET nom = %s, prenom = %s, email = %s WHERE id_user = %s",
                   (nom, prenom, email, user_id))
    conn.commit()
    cursor.close()
    conn.close()

def create_prestation(id_user, id_type_presta, debut, fin, adresse):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO prestation (id_user, debut_contrat, fin_contrat, adresse, status) VALUES (%s, %s, %s, %s, %s)",
                   (id_user, debut, fin, adresse, "En attente"))
    
    id_presta = cursor.lastrowid
    
    cursor.execute("INSERT INTO relation_type_presta (id_presta, id_type_presta) VALUES (%s, %s)",
                   (id_presta, id_type_presta))
    
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


