import psycopg2
from telebot import types

#Вспомогательные функции
from keyboards import create_inline_keyboard


# Параметры нашей БД (потом вынести в окружение)
db_params = {
    'dbname': 'watering_system',
    'user': 'postgres',
    'password': '1425',
    'host': 'localhost',
    'port': '5432',
}

######################### USERS #########################

# Функция для добавления юзера и контейнера в БД
def add_user(username):
   
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    try:
        # Проверяем есть ли такой юзер
        cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")
        existing_user = cursor.fetchone()

        # Если такого юзера нет, добавляем запись в таблицу + создаём контейнер
        if not existing_user:
            cursor.execute(f"INSERT INTO users (username) VALUES ('{username}')")
            cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")
            user_id = cursor.fetchone()[0]
            cursor.execute(f"INSERT INTO containers (user_id) VALUES ({user_id})")
            
    except Exception as e:
        print(f"Ошибка при выполнении запроса: {str(e)}")

    cursor.close()
    conn.commit()
    conn.close()


######################### PLANTS #########################

# Функция для добавления растения
def add_plant(username, name, relay_number):

    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    try:

        cursor.execute(f"""
            SELECT plants.*
            FROM plants
            INNER JOIN containers ON plants.container_id = containers.id
            INNER JOIN users ON containers.user_id = users.id
            WHERE plants.relay_number = {relay_number} AND users.username = '{username}';
        """)

        results = cursor.fetchall()
        
        if not results:
            # Находим id ёмкости
            cursor.execute(f"""
                SELECT containers.id
                FROM containers 
                JOIN users ON containers.user_id = users.id
                WHERE users.username = '{username}'
            """)
            container_id = cursor.fetchone()[0]  

            # Создаём новую запись в plants
            cursor.execute(f"INSERT INTO plants (name, relay_number, container_id) VALUES ('{name}', {relay_number}, {container_id})")

    except Exception as e:
        print(f"Ошибка при выполнении запроса: {str(e)}")

    cursor.close()
    conn.commit()
    conn.close()
    


# Функция для получения списка растений
def get_plants_buttons(username, action):
    
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    keyboard = None

    try:
        cursor.execute(f"""
            SELECT plants.id, plants.name
            FROM plants
            JOIN containers ON plants.container_id = containers.id
            JOIN users ON containers.user_id = users.id
            WHERE users.username = '{username}'
            """)
        plants = cursor.fetchall()

        if action in ('water', 'info') and plants:
            keyboard = create_inline_keyboard(plants, action)


    except Exception as e:
        print(f"Ошибка при выполнении запроса: {str(e)}")
    
    cursor.close()
    conn.close()
    
    return keyboard

# Функция для получения интересующих полей записи о растении
def get_plant(id, params):

    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    column_names = ', '.join([f'plants.{param}' for param in params])
    
    try:
        cursor.execute(f"""
            SELECT {column_names}
            FROM plants
            WHERE plants.id = '{id}'
            """)
        plant = cursor.fetchone()

    except Exception as e:
        print(f"Ошибка при выполнении запроса: {str(e)}")
        plant = None
    
    cursor.close()
    conn.close()
    
    return plant





