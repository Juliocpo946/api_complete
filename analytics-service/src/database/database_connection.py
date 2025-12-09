import pymysql
from src.config.config import config

def get_connection():
    return pymysql.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
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