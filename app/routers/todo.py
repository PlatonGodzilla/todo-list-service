from app.deps import cookie_params, BasicVerifier, SessionData, cookie, backend, verifier
from app import db
from app.services.todo_service import get_todo_data, insert_todo_data, get_file, delete_todo, get_shared_data
from sqlite3 import Connection
from fastapi import FastAPI, Form, Request, Depends, HTTPException, Response, File, UploadFile, APIRouter
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from app.templates import templates
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters
from fastapi_sessions.backends.implementations import InMemoryBackend
from fastapi_sessions.session_verifier import SessionVerifier
from uuid import UUID, uuid4
from pydantic import BaseModel
import os
from pathlib import Path
from typing import Annotated
import base64
import hashlib
import requests

app = FastAPI()
router = APIRouter()

@router.get("/addTodo")
def formPage(
    request: Request
):
    return templates.TemplateResponse("addTodoForm.html", {"request": request})

@router.post("/addTodo")
async def todo(
    request: Request,
    file: Annotated[UploadFile, File()],
    title: str = Form(),
    todo: str = Form(),
    url: str = Form(),
    conn=Depends(db.get_db),
    session_id=Depends(cookie),
    session_data: SessionData = Depends(verifier)
):
    if session_data == None:
        return RedirectResponse("/login", status_code=302)

    user_data = session_data
    share_id = str(uuid4())

    if url != '' and file.filename != '':
        return templates.TemplateResponse("addTodoForm.html", {
                "request": request,
                "error_message": "нельзя использовать 2 метода сразу"
            })

    if url == '' and file.filename == '':
            return templates.TemplateResponse("addTodoForm.html", {
                "request": request,
                "error_message": "Добавьте фото"
            })

    if url != '':
        r = requests.get(url)
        file_content = r.content

    if file.filename != '':
        file_content = await file.read()

    file_path = f"images/{uuid4()}"
    with open(file_path, "wb") as buffer:
        buffer.write(file_content)
    insert_todo_data(conn, file_path, title, todo, share_id, user_data.id)
    return RedirectResponse("/", status_code=302)

@router.get('/p/{share_id}')
def SharePost(
    share_id: str,
    request: Request,
    conn=Depends(db.get_db)
):
    shared_content = get_shared_data(conn, share_id)
    if shared_content is None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    
    pic = shared_content.file
    Title = shared_content.title
    formatted_data = shared_content.todo

    print(pic)
    if not(os.path.exists(pic)):
        pic = ''
    return templates.TemplateResponse("SharePost.html", {
        "request": request,
        "image": pic,
        "Title": Title,
        "note": formatted_data
        },
    ) 
@router.get('/', response_class=HTMLResponse)
async def index(request: Request, conn=Depends(db.get_db), session_id=Depends(cookie), session_data: SessionData = Depends(verifier)):
    user_data = session_data
    if user_data == None:
        return RedirectResponse("login")

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
    
    return templates.TemplateResponse("main.html", {
        "request": request,
        "items": items,
        "username": user_data.username
    })

@router.get('/download-file/{item_SHARE_ID}')
async def download(item_SHARE_ID: str, request: Request, conn=Depends(db.get_db)):
    file_path = get_file(conn, item_SHARE_ID)
    print(file_path[0])
    if os.path.exists(file_path[0]):
        return FileResponse(file_path[0], filename=f'{item_SHARE_ID}.png', media_type="application/octet-stream")
    else:
        return RedirectResponse(file_path[0], status_code=302)

@router.post('/delete/{item_SHARE_ID}')
async def delete(item_SHARE_ID: str, request: Request, conn=Depends(db.get_db)):
    file_path = get_file(conn, item_SHARE_ID)
    if os.path.exists(str(file_path[0])):
        os.remove(file_path[0])
    delete_todo(conn, item_SHARE_ID)
    return RedirectResponse("/", status_code=302)

@router.get("/debug-session")
async def debug_session(session_id: UUID = Depends(cookie)):
    session_data = await backend.read(session_id)
    return {
        "session_id": session_id,
        "session_data": session_data,
        "all_sessions": list(backend.data.keys())
    }