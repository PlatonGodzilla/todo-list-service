from app.deps import cookie_params, BasicVerifier, SessionData, cookie, backend, verifier
from app import db
from app.logic.users_logic import check_session_data, user_registration, status, login_user, logout_user
from fastapi import FastAPI, Form, Request, Depends, APIRouter
from fastapi.responses import RedirectResponse
from app.templates import templates
from uuid import UUID

app = FastAPI()
router = APIRouter()

@router.get("/register")
def registerPage(request: Request, session_id=Depends(cookie), session_data: SessionData = Depends(verifier)):
    if check_session_data(session_data):
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
def register(request: Request, conn=Depends(db.get_db), name: str = Form(), email: str = Form(), password: str = Form(), confirm_password: str = Form()):
    
    register_status = user_registration(conn, name, email, password, confirm_password)
    if register_status == status.PASSWORD_MISMATCH:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error_message": "ERROR: The passwords do not match"
        })
    if register_status == status.EMAIL_EXIST:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error_message": "ERROR: User already exist"
        })
    if register_status == status.OK:
        return RedirectResponse("/", status_code=302)
    
@router.get("/login")
def loginPage(request: Request, session_id=Depends(cookie), session_data: SessionData = Depends(verifier)):
    if check_session_data(session_data):
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(
    request: Request,
    email: str = Form(), 
    password: str = Form(),
    conn=Depends(db.get_db)
):

    login_status = await login_user(conn, email, password)
    
    if login_status == status.WRONG_DATA:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error_message": "Email or password is wrong"
        })
    else:
        response = RedirectResponse(url="/", status_code=302)
        cookie.attach_to_response(response, login_status)
        return response

@router.get("/logout")
async def logout(
    session_id: UUID = Depends(cookie)
):
    await logout_user(session_id)
    response = RedirectResponse("/")
    cookie.delete_from_response(response)
    return response
