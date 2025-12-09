import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', '123456'),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def execute_query(query, params=None):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchall()
        return result
    finally:
        connection.close()

def execute_file(filepath):
    connection = get_connection()
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        statements = sql_script.split(';')
        
        with connection.cursor() as cursor:
            for statement in statements:
                if statement.strip():
                    cursor.execute(statement)
        
        connection.commit()
        print(f"Ejecutado: {filepath}")
    finally:
        connection.close()