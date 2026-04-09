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


def get_last_5_techs():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.id_user, u.nom, u.prenom 
        FROM user u 
        INNER JOIN technicien t ON u.id_user = t.id_user 
        ORDER BY u.id_user DESC LIMIT 5
    """)
    techs = cursor.fetchall()
    cursor.close()
    conn.close()
    return techs

def get_all_techs():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.id_user, u.nom, u.prenom 
        FROM user u 
        INNER JOIN technicien t ON u.id_user = t.id_user
    """)
    techs = cursor.fetchall()
    cursor.close()
    conn.close()
    return techs

def get_last_5_prestas_by_status(status):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id_presta, status, adresse 
        FROM prestation 
        WHERE status = %s 
        ORDER BY id_presta DESC LIMIT 5
    """, (status,))
    prestas = cursor.fetchall()
    cursor.close()
    conn.close()
    return prestas

def get_presta_details(presta_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.*, c.nom as client_nom, c.prenom as client_prenom
        FROM prestation p
        LEFT JOIN user c ON p.id_user = c.id_user
        WHERE p.id_presta = %s
    """, (presta_id,))
    presta = cursor.fetchone()
    cursor.close()
    conn.close()
    return presta

def get_tech_details(tech_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user WHERE id_user = %s", (tech_id,))
    tech = cursor.fetchone()
    cursor.close()
    conn.close()
    return tech

# --- NOUVELLES REQUÊTES : AJOUT, ASSIGNATION, DÉTAILS ---

def add_technicien(nom, prenom, email, telephone, mdp):
    """Ajoute un nouveau technicien dans la base de données"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # 1. Insertion dans la table USER
        cursor.execute("""
            INSERT INTO user (nom, prenom, email, telephone, mdp) 
            VALUES (%s, %s, %s, %s, %s)
        """, (nom, prenom, email, telephone, mdp))
        nouvel_id = cursor.lastrowid
        
        # 2. Déclaration du rôle dans la table TECHNICIEN
        cursor.execute("INSERT INTO technicien (id_user) VALUES (%s)", (nouvel_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erreur lors de l'ajout du technicien : {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def assign_tech_to_presta(id_presta, id_tech):
    """Associe un technicien à une prestation et la passe en Confirmée"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Insertion dans la table de liaison DISPONIBILITE (selon ton MCD)
        cursor.execute("INSERT INTO disponibilite (id_user, id_presta) VALUES (%s, %s)", (id_tech, id_presta))
        
        # On passe le statut à "Confirmée" si elle était "En attente"
        cursor.execute("UPDATE prestation SET status = 'Confirmée' WHERE id_presta = %s AND status = 'En attente'", (id_presta,))
        conn.commit()
    except Exception as e:
        print(f"Erreur d'assignation : {e}")
    finally:
        cursor.close()
        conn.close()

def get_tech_latest_prestas(id_tech):
    """Récupère les 5 dernières prestations d'un technicien"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.id_presta, p.adresse, p.status 
        FROM prestation p
        INNER JOIN disponibilite d ON p.id_presta = d.id_presta
        WHERE d.id_user = %s
        ORDER BY p.id_presta DESC LIMIT 5
    """, (id_tech,))
    prestas = cursor.fetchall()
    cursor.close()
    conn.close()
    return prestas