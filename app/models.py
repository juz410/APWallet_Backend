from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String, Numeric, text, LargeBinary
from .database import Base
from sqlalchemy.orm import relationship

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
    sender_id = Column(String, ForeignKey('users.user_id'), nullable=True)
    receiver_id = Column(String, ForeignKey('users.user_id'), nullable=True)
    amount = Column(Numeric(precision=12, scale=2), nullable=False)
    transaction_method = Column(String, nullable=False)
    registered_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)
    card_id = Column(Integer, ForeignKey('cards.card_id'), nullable=True)
    
    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
    card = relationship("Card")

class Card(Base):
    __tablename__ = "cards"
    card_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    card_number = Column(String, nullable=False) #to be encrypted
    card_expire_month = Column(String, nullable=False) #to be encrypted
    card_expire_year = Column(String, nullable=False) #to be encrypted
    card_cvv = Column(String, nullable=False) #to be encrypted
    registered_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)

    user = relationship("User")