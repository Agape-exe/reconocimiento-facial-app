import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="31415",  
        database="reconocimiento_facial"
    )
