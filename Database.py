
import mysql.connector
from datetime import datetime, timedelta

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
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
        SELECT p.*, GROUP_CONCAT(tp.nom) AS types_presta
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

    def get_last_5_techs():
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT u.* FROM user u
            JOIN technicien t ON u.id_user = t.id_user
            ORDER BY u.id_user DESC LIMIT 5
        """)
        res = cursor.fetchall()
        cursor.close()
        conn.close()
        return res

def get_last_5_prestas_by_status(status):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.*, u.nom as client_nom, u.prenom as client_prenom 
        FROM prestation p
        JOIN user u ON p.id_user = u.id_user
        WHERE p.status = %s
        ORDER BY p.id_presta DESC LIMIT 5
    """, (status,))
    res = cursor.fetchall()
    cursor.close()
    conn.close()
    return res

def get_tech_latest_prestas(tech_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.id_presta, p.status, p.adresse 
        FROM prestation p
        JOIN disponibilite d ON p.id_presta = d.id_presta
        WHERE d.id_user = %s
        ORDER BY p.id_presta DESC LIMIT 10
    """, (tech_id,))
    res = cursor.fetchall()
    cursor.close()
    conn.close()
    return res

def get_presta_details(presta_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.*, u.nom as client_nom, u.prenom as client_prenom 
        FROM prestation p
        JOIN user u ON p.id_user = u.id_user
        WHERE p.id_presta = %s
    """, (presta_id,))
    res = cursor.fetchone()
    cursor.close()
    conn.close()
    return res

def add_technicien(nom, prenom, email, tel, mdp):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO user (nom, prenom, email, telephone, mdp) VALUES (%s, %s, %s, %s, %s)",
                       (nom, prenom, email, tel, mdp))
        nouvel_id = cursor.lastrowid
        cursor.execute("INSERT INTO technicien (id_user) VALUES (%s)", (nouvel_id,))
        conn.commit()
        return True
    except:
        return False
    finally:
        cursor.close()
        conn.close()
def get_last_5_techs():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.* FROM user u
        JOIN technicien t ON u.id_user = t.id_user
        ORDER BY u.id_user DESC LIMIT 5
    """)
    res = cursor.fetchall()
    cursor.close()
    conn.close()
    return res

def get_last_5_prestas_by_status(status):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.*, u.nom as client_nom, u.prenom as client_prenom 
        FROM prestation p
        JOIN user u ON p.id_user = u.id_user
        WHERE p.status = %s
        ORDER BY p.id_presta DESC LIMIT 5
    """, (status,))
    res = cursor.fetchall()
    cursor.close()
    conn.close()
    return res

def get_tech_latest_prestas(tech_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.id_presta, p.status, p.adresse 
        FROM prestation p
        JOIN disponibilite d ON p.id_presta = d.id_presta
        WHERE d.id_user = %s
        ORDER BY p.id_presta DESC LIMIT 10
    """, (tech_id,))
    res = cursor.fetchall()
    cursor.close()
    conn.close()
    return res

def get_presta_details(presta_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.*, c.nom as client_nom, c.prenom as client_prenom,
               tp.nom,
               tech_u.prenom as tech_prenom, tech_u.nom as tech_nom
        SELECT p.*, u.nom as client_nom, u.prenom as client_prenom 
        FROM prestation p
        LEFT JOIN user c ON p.id_user = c.id_user
        LEFT JOIN relation_type_presta rtp ON p.id_presta = rtp.id_presta
        LEFT JOIN type_presta tp ON rtp.id_type_presta = tp.id_type_presta
        LEFT JOIN disponibilite d ON p.id_presta = d.id_presta
        LEFT JOIN user tech_u ON d.id_user = tech_u.id_user
        JOIN user u ON p.id_user = u.id_user
        WHERE p.id_presta = %s
    """, (presta_id,))
    prestas = cursor.fetchall()
    res = cursor.fetchone()
    cursor.close()
    conn.close()
    return prestas[0] if prestas else None

def get_tech_details(tech_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user WHERE id_user = %s", (tech_id,))
    tech = cursor.fetchone()
    cursor.close()
    conn.close()
    return tech

def add_technicien(nom, prenom, email, tel, mdp):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO user (nom, prenom, email, telephone, mdp) VALUES (%s, %s, %s, %s, %s)",
                       (nom, prenom, email, tel, mdp))
        nouvel_id = cursor.lastrowid
        cursor.execute("INSERT INTO technicien (id_user) VALUES (%s)", (nouvel_id,))
        conn.commit()
        return True
    except:
        return False
    finally:
        cursor.close()
        conn.close()

def refuser_prestation(presta_id):
    """Passe le status d'une prestation à Annulée"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE prestation SET status = 'Annulée' WHERE id_presta = %s", (presta_id,))
        conn.commit()
    except Exception as e:
        print(f"Erreur lors du refus de la prestation : {e}")
    finally:
        cursor.close()
        conn.close()

def assign_tech_to_presta(id_presta, id_tech):
    """Associe un technicien à une prestation et la passe en Confirmée"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Insertion dans la table de liaison DISPONIBILITE (selon le MCD)
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

def get_tech_prestas_with_dates(id_tech):
    """Récupère toutes les prestations d'un technicien avec leurs dates pour le calendrier"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.id_presta, p.debut_contrat, p.fin_contrat, p.status, p.adresse
        FROM prestation p
        INNER JOIN disponibilite d ON p.id_presta = d.id_presta
        WHERE d.id_user = %s
        ORDER BY p.debut_contrat
    """, (id_tech,))
    prestas = cursor.fetchall()
    cursor.close()
    conn.close()
    return prestas

