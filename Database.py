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