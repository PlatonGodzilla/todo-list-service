from app.deps import cookie_params, BasicVerifier, cookie, backend, verifier, User
from app import db
from app.logic.todo_logic import status, post_todo, shared_todo, get_todo, download_post, delete_post
from fastapi import FastAPI, Form, Request, Depends, HTTPException, File, UploadFile, APIRouter
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from app.templates import templates
from uuid import UUID
from typing import Annotated

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
    session_data: User = Depends(verifier)
):
    post_todo_status = await post_todo(conn, file, title, todo, url, session_data)
    if post_todo_status == status.SESSION_NOT_FOUND:
        return RedirectResponse("/login", status_code=302)

    if post_todo_status == status.EMPTY_FILE:
        return templates.TemplateResponse("addTodoForm.html", {
                "request": request,
                "error_message": "нельзя использовать 2 метода сразу"
            })

    if post_todo_status == status.TOO_MANY_REQUESTS:
            return templates.TemplateResponse("addTodoForm.html", {
                "request": request,
                "error_message": "Добавьте фото"
            })
    
    if post_todo_status == status.OK:
        return RedirectResponse("/", status_code=302)

@router.get('/p/{share_id}')
def SharePost(
    share_id: str,
    request: Request,
    conn=Depends(db.get_db)
):
    shared_todo_status = shared_todo(conn, share_id)
    if shared_todo_status["status"] == status.MISSING_CONTENT:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if shared_todo_status["status"] == status.OK:
        return templates.TemplateResponse("SharePost.html", {
        "request": request,
        "image": shared_todo_status["pic"],
        "Title": shared_todo_status["Title"],
        "note": shared_todo_status["formatted_data"]
        }, 
    ) 
@router.get('/', response_class=HTMLResponse)
async def index(request: Request, conn=Depends(db.get_db), session_id=Depends(cookie), session_data: User = Depends(verifier)):
    get_todo_status = get_todo(conn, session_data)
    if get_todo_status["status"] == status.SESSION_NOT_FOUND:
        return RedirectResponse("login")

    if get_todo_status["status"] == status.OK:
        return templates.TemplateResponse("main.html", {
            "request": request,
            "items": get_todo_status["items"],
            "username": get_todo_status["username"]
        })

@router.get('/download-file/{item_SHARE_ID}')
def download(item_SHARE_ID: str, request: Request, conn=Depends(db.get_db)):
    download_post_status = download_post(conn, item_SHARE_ID)
    if download_post_status["status"] == status.OK:
        return FileResponse(download_post_status["file_path"], filename=f'{item_SHARE_ID}.png', media_type="application/octet-stream")
    
    if download_post_status["status"] == status.MISSING_CONTENT:
        return RedirectResponse(download_post_status["file_path"], status_code=302)

@router.post('/delete/{item_SHARE_ID}')
async def delete(item_SHARE_ID: str, request: Request, conn=Depends(db.get_db)):
    delete_post_status = delete_post(conn, item_SHARE_ID)
    if delete_post_status["status"] == status.OK:
        return RedirectResponse("/", status_code=302)

@router.get("/debug-session")
async def debug_session(session_id: UUID = Depends(cookie)):
    session_data = await backend.read(session_id)
    return {
        "session_id": session_id,
        "session_data": session_data,
        "all_sessions": list(backend.data.keys())
    }