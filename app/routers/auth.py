from app.deps import cookie_params, BasicVerifier, SessionData, cookie, backend, verifier
from app import db
from app.services.users_service import get_user_data, insert_user_data
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

@router.get("/register")
def registerPage(request: Request, session_id=Depends(cookie), session_data: SessionData = Depends(verifier)):
    if session_data != None:
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
def register(request: Request, conn=Depends(db.get_db), name: str = Form(), email: str = Form(), password: str = Form(), confirm_password: str = Form()):
    
    hash_pass = hashlib.sha256(password.encode('utf-8'))
    hash_confirm_pass = hashlib.sha256(confirm_password.encode('utf-8'))

    if hash_pass.hexdigest() != hash_confirm_pass.hexdigest():
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error_message": "ERROR: The passwords do not match"
        })

    
    print(get_user_data(conn, email, None))
    if get_user_data(conn, email, password=None):
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error_message": "ERROR: User with this email already exists"
        })
    

    insert_user_data(conn, name, email, hash_pass.hexdigest())
    print(get_user_data(conn, email, password=None))
    return RedirectResponse("/", status_code=302)

@router.get("/login")
def loginPage(request: Request, session_id=Depends(cookie), session_data: SessionData = Depends(verifier)):
    if session_data != None:
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(
    request: Request,
    email: str = Form(), 
    password: str = Form(),
    conn=Depends(db.get_db)
):
    hash_pass = hashlib.sha256(password.encode('utf-8')).hexdigest()
    print(get_user_data(conn, email, hash_pass))
    user = get_user_data(conn, email, hash_pass)
    
    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error_message": "Email or password is wrong"
        })
    else:
        session_id = uuid4()
        session_data = SessionData(id=user[0], username=user[1], email=user[2])
        
        await backend.create(session_id, session_data)
        
        response = RedirectResponse(url="/", status_code=302)
        cookie.attach_to_response(response, session_id)
        return response

@router.get("/logout")
async def logout(
    session_id: UUID = Depends(cookie)
):
    await backend.delete(session_id)
    response = RedirectResponse("/")
    cookie.delete_from_response(response)
    return response
