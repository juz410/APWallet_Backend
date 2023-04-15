from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from enum import Enum

class TransactionMethod(str, Enum):
    CARD_TOPUP = "card_topup"
    ONLINE_BANKING = "online_banking"
    INSTANT_TRANSFER = "instant_transfer"


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


class CardCreate(BaseModel):
    card_number : str
    card_expire_month : str
    card_expire_year : str
    card_cvv : str

class CardOut(BaseModel):
    card_id : int
    card_number : str
    registered_at : datetime
    user: User
    class Config:
        orm_mode = True

class TransactionBase(BaseModel):
    sender_id : Optional [str] = None
    receiver_id : Optional [str] = None
    amount : float
    transaction_method : TransactionMethod
    card_id : Optional[int] = None
    last_4_card_digits : Optional[str] = None

class TransactionCreate(TransactionBase):
    pin_number: Optional[str] = None

class TransactionOut(TransactionBase):
    transaction_id : int
    registered_at : datetime
    sender : Optional[User]
    receiver : Optional[User]
    card : Optional[CardOut]
    class Config:
        orm_mode = True

class ChangePinRequest(BaseModel):
    otp: str
    new_pin: str
    