from pydantic import BaseModel


class Todo(BaseModel):
    id: int
    file: str
    title: str
    todo: str
    share_id: str
    user_id: int