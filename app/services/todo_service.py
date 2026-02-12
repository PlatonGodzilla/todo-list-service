from sqlite3 import Connection
from app.models.todo_model import Todo
from app.models.users_model import User
def get_todo_data(conn: Connection,
                  session_id: int,
                  ):
    cursor = conn.cursor()

    cursor.execute('SELECT id, file, title, todo, share_id FROM todo WHERE user_id = ?', (session_id, ))
    items = cursor.fetchall()
    return [Todo(id = item[0],
                file=item[1],
                title=item[2],
                todo=item[3],
                share_id=item[4])
            for item in items
]

def get_shared_data(conn: Connection,
                    share_id: str):
    cursor = conn.cursor()

    cursor.execute("SELECT file, title, todo, share_id FROM todo WHERE share_id = ?", (share_id, ))
    item = cursor.fetchone()
    return Todo(file=item[0],
                title=item[1],
                todo=item[2],
                share_id=item[3],
                id=None
                )


def insert_todo_data(conn: Connection,
                    file_path: str,
                    title: str,
                    todo: str,
                    share_id: str,
                    session_id: int):
    cursor = conn.cursor()
    cursor.execute('INSERT INTO todo (file, title, todo, share_id, user_id) VALUES (?, ?, ?, ?, ?)', (file_path, title, todo, share_id, session_id))

    return conn.commit()


def get_file(conn: Connection,
             share_id: str):
    cursor = conn.cursor()
    cursor.execute('SELECT file FROM todo WHERE share_id = ?', (share_id, ))
    return cursor.fetchone()

def delete_todo(conn: Connection,
                share_id: str):
     cursor = conn.cursor()
     cursor.execute('DELETE FROM todo WHERE share_id = ?', (share_id, ))
     return conn.commit()