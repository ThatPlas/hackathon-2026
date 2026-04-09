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
    cursor.execute("INSERT INTO user (nom, prenom, email, mdp) VALUES (%s, %s, %s, %s)",
                   (nom, prenom, email, mdp))
    conn.commit()
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

# --- Dans Database.py ---

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

def get_services_by_category(category_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True) 
    
    query = "SELECT nom, description, prix FROM type_presta WHERE id_categorie = %s"
    cursor.execute(query, (category_id,))
    
    services = cursor.fetchall()
    cursor.close()
    conn.close()
    return services

def get_type_prestas_by_category(category_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM type_presta WHERE id_categorie = %s", (category_id,))
    type_prestas = cursor.fetchall()
    cursor.close()
    conn.close()
    return type_prestas


def delete_prestation(id_presta):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM prestation WHERE id_presta = %s", (id_presta,))
    conn.commit()
    cursor.close()
    conn.close()


def get_user_panier(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT tp.nom, tp.prix, p.id_presta, p.debut_contrat 
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