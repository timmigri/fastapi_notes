from pydantic import BaseModel
from typing import Optional

class NoteCreate(BaseModel):
    name: str
    description: Optional[str] = None

class NoteResponse(NoteCreate):
    id: int