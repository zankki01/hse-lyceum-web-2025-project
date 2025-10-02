from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional
class UserBase(BaseModel):
    email: EmailStr
    login: str = Field(..., min_length=3, max_length=50)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
class UserUpdate(BaseModel):
    email: Optional[EmailStr]
    login: Optional[str]
    password: Optional[str]
class UserOut(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

class PostBase(BaseModel):
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)

class PostCreate(PostBase):
    author_id: int

class PostUpdate(BaseModel):
    title: Optional[str]
    content: Optional[str]

class PostOut(PostBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime