from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String, Numeric, text, func
from .database import Base

class User(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    phone_number = Column(String, unique=True, nullable=False)
    balance = Column(Numeric(precision=12, scale=2), server_default=text("0"))
    pin_number = Column(String, nullable=False)
    registered_at = Column(TIMESTAMP(timezone=True), server_default=text('now()') , nullable=False)


class Transaction(Base):
    __tablename__ = "transactions"
    transaction_id = Column(Integer, primary_key=True, autoincrement=True)
    sender_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    receiver_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    amount = Column(Numeric(precision=12, scale=2), nullable=False)
    datetime = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)
    transaction_method = Column(String, nullable=False)

class Card(Base):
    __tablename__ = "cards"
    card_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    card_number = Column(String, nullable=False) #to be encrypted
    card_expire_month = Column(String, nullable=False) #to be encrypted
    card_expire_year = Column(String, nullable=False) #to be encrypted
    card_cvv = Column(String, nullable=False) #to be encrypted