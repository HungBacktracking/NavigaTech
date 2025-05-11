from datetime import datetime

from pydantic import BaseModel



class SessionCreate(BaseModel):
    title: str

class SessionResponse(BaseModel):
    id: str
    title: str

class MessageCreate(BaseModel):
    role: str # user|assistant
    content: str

class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    timestamp: datetime