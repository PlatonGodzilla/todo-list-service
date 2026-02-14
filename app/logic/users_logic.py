from app.deps import cookie_params, BasicVerifier, User, cookie, backend, verifier
from app import db
from app.services.users_service import get_user_data, insert_user_data
from uuid import UUID, uuid4
import hashlib
from sqlite3 import Connection
import enum

class status(enum.Enum):
    OK = 0
    PASSWORD_MISMATCH = 1
    EMAIL_EXIST = 2
    WRONG_DATA = 3

def check_session_data(
                       session_data: User
                       ):
    if session_data != None:
        return True
        


def user_registration(
                      conn: Connection,
                      name: str,
                      email: str,
                      password: str,
                      confirm_password: str
                      ):

    hash_pass = hashlib.sha256(password.encode('utf-8'))

    if password != confirm_password:
        return status.PASSWORD_MISMATCH

    
    if get_user_data(conn, email, password=None):
        return status.EMAIL_EXIST
    

    insert_user_data(conn, name, email, hash_pass.hexdigest())
    return status.OK


async def login_user(
        conn: Connection,
        email: str,
        password: str
):
    hash_pass = hashlib.sha256(password.encode('utf-8')).hexdigest()
    user = get_user_data(conn, email, hash_pass)
    
    if not user:
        return status.WRONG_DATA
    else:
        session_id = uuid4()
        session_data = User(id=user.id, username=user.username, email=user.email)
        
        await backend.create(session_id, session_data)
        

        return session_id
        
async def logout_user(
        session_id: UUID
):
    return await backend.delete(session_id)
