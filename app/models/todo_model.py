from pydantic import BaseModel
from typing import Optional


class Todo(BaseModel):
    id: Optional[int]
    file: str
    title: str
    todo: str
    share_id: str