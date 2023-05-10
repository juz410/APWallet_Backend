from ..utils import hash_utils, crypto_utils, rsa_utils
from .. import models, schemas, cas
from fastapi import HTTPException, status, Depends, APIRouter
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from typing import List
from decimal import Decimal

router = APIRouter(
    prefix="/transaction",
    tags=["transaction"],
)

@router.post("/",status_code=status.HTTP_201_CREATED, response_model=schemas.TransactionOut, description="Note: User's PIN Number and Transaction Amount must be encrypted")
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
        
        
    if transaction.transaction_method == schemas.TransactionMethod.CARD_TOPUP:
        card = db.query(models.Card).filter(models.Card.card_id == transaction.card_id).first()
        if(not card):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
        if(card.user_id != sender_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to topup with this card")
        transaction.card_id = card.card_id
        card_number_last_4_digits = crypto_utils.decrypt(card.card_number)[-4:]
        transaction.last_4_card_digits = card_number_last_4_digits

    if transaction.transaction_method == schemas.TransactionMethod.INSTANT_TRANSFER:

        try:
            decrypted_secret_key = rsa_utils.decrypt_secret_key(transaction.aes_key.key)
            decrypted_iv = rsa_utils.decrypt_secret_key(transaction.aes_key.iv)
            # transaction.amount = float(rsa_utils.decrypt_aes_encryption(transaction.amount, decrypted_secret_key, decrypted_iv))
            transaction.pin_number = rsa_utils.decrypt_aes_encryption(transaction.pin_number, decrypted_secret_key, decrypted_iv)
            if(not hash_utils.verify(transaction.pin_number, user.pin_number)):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Pin Number")
          
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error decrypting data")

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
    del transaction.aes_key
    trasaction_dict = transaction.dict()
    trasaction_dict.pop("pin_number")
    transaction = models.Transaction(**trasaction_dict)
    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction

@router.get("/", response_model=List[schemas.TransactionOut])
def get_transactions(db: Session = Depends(get_db), cas_user = Depends(cas.cas_service_ticket_validator), 
                     sender_id: str = None, receiver_id: str = None, transaction_method: str = None):

    if(cas_user['role'] != "staff"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to view all transactions")

    if sender_id and receiver_id:
        sender = db.query(models.User).filter(models.User.user_id == sender_id).first()
        if(not sender):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sender not found")
        receiver = db.query(models.User).filter(models.User.user_id == receiver_id).first()
        if(not receiver):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receiver not found")
        transactions = db.query(models.Transaction).filter(
            models.Transaction.sender_id == sender_id, 
            models.Transaction.receiver_id == receiver_id,
            models.Transaction.transaction_method == transaction_method).order_by(desc(
            models.Transaction.registered_at)).all()
        return transactions
    
    if sender_id:
        sender = db.query(models.User).filter(
            models.User.user_id == sender_id, models.Transaction.transaction_method == transaction_method).first()
        if(not sender):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sender not found")
        transactions = db.query(models.Transaction).filter(
            models.Transaction.sender_id == sender_id).order_by(desc(
            models.Transaction.registered_at)).all()
        return transactions

    if receiver_id:
        receiver = db.query(models.User).filter(
            models.User.user_id == receiver_id,
            models.Transaction.transaction_method == transaction_method).first()
        if(not receiver):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receiver not found")
        transactions = db.query(models.Transaction).filter(
            models.Transaction.receiver_id == receiver_id).order_by(desc(
            models.Transaction.registered_at)).all()
        return transactions
    

    transactions = db.query(models.Transaction).filter(
                        models.Transaction.transaction_method == transaction_method).order_by(desc(
                        models.Transaction.registered_at)).all()
    return transactions

@router.get("/user", response_model=List[schemas.TransactionOut])
def get_user_transactions(db: Session = Depends(get_db), cas_user = Depends(cas.cas_service_ticket_validator),
                          page: int = 0):
    
    limit = 7
    offset = page * limit
    
    user_id = cas_user['user_id']
    transactions = db.query(models.Transaction).filter(
        or_(models.Transaction.sender_id == user_id, 
            models.Transaction.receiver_id == user_id)).order_by(desc(
        models.Transaction.registered_at)).limit(limit=limit).offset(offset=offset).all()
    return transactions