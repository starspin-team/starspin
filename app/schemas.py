from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: int
    username: str
    stars: float
    created_at: datetime

    class Config:
        from_attributes = True

class BetCreate(BaseModel):
    amount: float = Field(..., gt=0)
    segment: str

class BetResponse(BaseModel):
    id: int
    amount: float
    segment: str
    result: str
    win_amount: float
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None 