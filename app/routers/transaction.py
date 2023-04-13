from ..utils import hash_utils
from .. import models, schemas, cas
from fastapi import HTTPException, status, Depends, APIRouter
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List
from decimal import Decimal

router = APIRouter(
    prefix="/transaction",
    tags=["transaction"],
)

@router.post("/",status_code=status.HTTP_201_CREATED, response_model=schemas.TransactionOut)
def create_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db), cas_user = Depends(cas.cas_service_ticket_validator)):
    sender_id = cas_user['user_id']
    transaction.amount = Decimal(transaction.amount)
    if transaction.transaction_method in (schemas.TransactionMethod.CARD_TOPUP, schemas.TransactionMethod.ONLINE_BANKING):
        transaction.sender_id = None
        transaction.receiver_id = cas_user['user_id']
    elif transaction.transaction_method == schemas.TransactionMethod.INSTANT_TRANSFER:
        if not(transaction.pin_number):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Pin number is required for instant transfer")
        user = db.query(models.User).filter(models.User.user_id == sender_id).first()
        if(not user):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if(not hash_utils.verify(transaction.pin_number, user.pin_number)):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Pin Number")
        
    if transaction.transaction_method == schemas.TransactionMethod.CARD_TOPUP:
        card = db.query(models.Card).filter(models.Card.card_id == transaction.card_id).first()
        if(not card):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
        if(card.user_id != sender_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to topup with this card")
        transaction.card_id = card.card_id

    if transaction.transaction_method == schemas.TransactionMethod.INSTANT_TRANSFER:
        if not transaction.receiver_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Receiver id is required for instant transfer")
        if transaction.receiver_id == sender_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot transfer to yourself")
        receiver = db.query(models.User).filter(models.User.user_id == transaction.receiver_id).first()
        if(not receiver):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receiver not found")
        sender_balance = db.query(models.User).filter(models.User.user_id == sender_id).first().balance
        if(sender_balance - transaction.amount < 0):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance")
        transaction.receiver_id = receiver.user_id
        transaction.sender_id = sender_id

    sender_query = db.query(models.User).filter(models.User.user_id == transaction.sender_id)
    receiver_query = db.query(models.User).filter(models.User.user_id == transaction.receiver_id)

    sender = sender_query.first()
    receiver = receiver_query.first()
    if sender:
        sender.balance -= transaction.amount
        db.query(models.User).filter(models.User.user_id == transaction.sender_id).update({"balance": sender.balance})

    if receiver:
        receiver.balance += transaction.amount
        db.query(models.User).filter(models.User.user_id == transaction.receiver_id).update({"balance": receiver.balance})

    trasaction_dict = transaction.dict()
    trasaction_dict.pop("pin_number")
    transaction = models.Transaction(**trasaction_dict)
    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction

@router.get("/", response_model=List[schemas.TransactionOut])
def get_transactions(db: Session = Depends(get_db), cas_user = Depends(cas.cas_service_ticket_validator), sender_id: str = None, receiver_id: str = None):
    print(sender_id)
    print(receiver_id)
    if(cas_user['role'] != "staff"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to view all transactions")

    if sender_id:
        transactions = db.query(models.Transaction).filter(models.Transaction.sender_id == sender_id).all()
        return transactions

    if receiver_id:
        transactions = db.query(models.Transaction).filter(models.Transaction.receiver_id == receiver_id).all()
        return transactions
    
    if sender_id and receiver_id:
        transactions = db.query(models.Transaction).filter(models.Transaction.sender_id == sender_id, models.Transaction.receiver_id == receiver_id).all()
        return transactions

    transactions = db.query(models.Transaction).all()
    return transactions

@router.get("/user", response_model=List[schemas.TransactionOut])
def get_user_transactions(db: Session = Depends(get_db), cas_user = Depends(cas.cas_service_ticket_validator)):
    user_id = cas_user['user_id']
    transactions = db.query(models.Transaction).filter(or_(models.Transaction.sender_id == user_id, models.Transaction.receiver_id == user_id)).all()
    return transactions