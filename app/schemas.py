from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    pin_number : str
    phone_number : str

class User(BaseModel):
    user_id : str
    email : EmailStr
    name : str
    phone_number : str
    balance : float
    registered_at : datetime
    class Config:
        orm_mode = True

class UserClass(User):
    pin_number: str

    