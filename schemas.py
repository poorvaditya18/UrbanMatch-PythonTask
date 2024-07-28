from pydantic import BaseModel , EmailStr
from typing import List

class EmailValidationModel(BaseModel):
    email: EmailStr 
class UserBase(BaseModel):
    name: str
    age: int
    gender: str
    # email: str
    email : EmailStr
    city: str
    interests: List[str]
    class Config:
        from_attributes = True
class UserCreate(UserBase):
    pass
class User(UserBase):
    id: int
    class Config:
        orm_mode = True
        from_attributes = True

