from app.routers import todo, auth
from app import db
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path


if not os.path.exists('images'):
    os.makedirs('images')
UPLOAD_DIR = Path("images")


TEMPLATES_DIR = Path("templates")
if not TEMPLATES_DIR.is_dir():
    raise Exception("There isn't template direcotory")

#БД________________________________________________________
db.create_db_if_not_exist()


app = FastAPI()
#роуты________________________________________________________

app.include_router(todo.router)
app.include_router(auth.router)



print(TEMPLATES_DIR.absolute())
app.mount("/templates", StaticFiles(directory=TEMPLATES_DIR.absolute()))
app.mount("/images", StaticFiles(directory=str(UPLOAD_DIR)), name="images")
app.mount("/static", StaticFiles(directory="static"), name="static")
 