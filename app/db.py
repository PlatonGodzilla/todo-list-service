import sqlite3


def create_db_if_not_exist():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usrs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS todo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file LONGBLOB,
            title TEXT NOT NULL,
            todo TEXT NOT NULL,
            share_id TEXT UNIQUE,
            user_id INTEGER REFERENCES usrs(id)
        )
    ''')
    conn.commit()
    
def get_db():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()
