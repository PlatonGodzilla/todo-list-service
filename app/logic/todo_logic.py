from app.deps import cookie_params, BasicVerifier, SessionData, cookie, backend, verifier
from app.services.todo_service import get_todo_data, insert_todo_data, get_file, delete_todo, get_shared_data
from fastapi import File, UploadFile
from uuid import uuid4
import os
from sqlite3 import Connection
from typing import Annotated
import requests
import enum

class status(enum.Enum):
    OK = 0,
    EMPTY_FILE = 1
    TOO_MANY_REQUESTS = 2
    SESSION_NOT_FOUND = 3 
    MISSING_CONTENT = 4


async def post_todo(
        conn: Connection,
        file: Annotated[UploadFile, File()],
        title: str,
        todo: str,
        url: str,
        session_data: SessionData,

):
    
    user_data = session_data
    share_id = str(uuid4())

    if session_data == None:
        return status.SESSION_NOT_FOUND

    if url != '' and file.filename != '':
        return status.EMPTY_FILE

    if url == '' and file.filename == '':
            return status.TOO_MANY_REQUESTS

    if url != '':
        r = requests.get(url)
        file_content = r.content

    if file.filename != '':
        file_content = await file.read()

    file_path = f"images/{uuid4()}"
    with open(file_path, "wb") as buffer:
        buffer.write(file_content)
    insert_todo_data(conn, file_path, title, todo, share_id, user_data.id)
    return status.OK

def shared_todo(
        conn: Connection,
        share_id: str
):
    shared_content = get_shared_data(conn, share_id)
    if shared_content is None:
        return {"status": status.MISSING_CONTENT}
    
    
    pic = shared_content.file
    Title = shared_content.title
    formatted_data = shared_content.todo
    
    if not(os.path.exists(pic)):
        pic = ''
    return {"pic": pic, "Title": Title, "formatted_data": formatted_data, "status": status.OK}

def get_todo(
        conn: Connection,
        session_data: SessionData
):
    user_data = session_data
    if user_data == None:
        return {"status": status.SESSION_NOT_FOUND}

    todos = get_todo_data(conn, user_data.id)
        
    id = []
    Title = []
    formatted_data = []
    decoded_images = []
    share_ID = []
    for todo_item in todos:
        id.append(todo_item.id)
        Title.append(todo_item.title)
        formatted_data.append(todo_item.todo) 
        decoded_images.append(todo_item.file)
        share_ID.append(todo_item.share_id)

    items = []

    for id, title, note, img, share_id in zip(id, Title, formatted_data, decoded_images, share_ID):
        items.append({"id": id, "title": title, "note": note, "img": img, "SHARE_ID": share_id})
    
    return {"items": items, "username": user_data.username, "status": status.OK}

def download_post(
        conn: Connection,
        item_SHARE_ID: str
):
    file_path = get_file(conn, item_SHARE_ID)
    if os.path.exists(file_path[0]):
        return {"file_path": file_path[0],"status": status.OK}
    else:
        return {"file_path": file_path[0],"status": status.MISSING_CONTENT}
    
def delete_post(
        conn: Connection,
        item_SHARE_ID: str
):
    file_path = get_file(conn, item_SHARE_ID)
    if os.path.exists(str(file_path[0])):
        os.remove(file_path[0])
    delete_todo(conn, item_SHARE_ID)
    return {"status": status.OK}