from sqlite3 import Connection
from app.models.users_model import User

def get_user_data(conn: Connection,
                    email: str, 
                    password = None):
    cursor = conn.cursor()

    if password is None:
        cursor.execute('SELECT email FROM usrs WHERE email = ?', (email,))
    else:
        cursor.execute("SELECT id, name, email FROM usrs WHERE email = ? AND password = ?", (email, password))

    return cursor.fetchone()


def insert_user_data(conn: Connection,
                     name: str,
                     email: str,
                     password: str):
    cursor = conn.cursor()

    cursor.execute('INSERT INTO usrs (name, email, password) VALUES (?, ?, ?)', (name, email, password))

    return conn.commit()
