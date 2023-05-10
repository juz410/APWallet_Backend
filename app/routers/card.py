from ..utils import crypto_utils, rsa_utils
from .. import models, schemas, cas
from fastapi import HTTPException, status, Depends, APIRouter
from ..database import get_db
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(
    prefix="/card",
    tags=["card"],
)

@router.get("/", response_model=List[schemas.CardOut])
def get_cards(db: Session = Depends(get_db), cas_user = Depends(cas.cas_service_ticket_validator)):
    cas_user_id = cas_user['user_id']
    cards = db.query(models.Card).filter(models.Card.user_id == cas_user_id).all()
    if(not cards):
        return []

    for card in cards:
        card.card_number = crypto_utils.decrypt(card.card_number)

    return cards
    

@router.post("/", response_model=schemas.CardOut, description="Note: Card Details must be encrypted")
def add_card(card: schemas.CardCreate, db: Session = Depends(get_db), cas_user = Depends(cas.cas_service_ticket_validator)):
    
    cas_user_id = cas_user['user_id']

    try:
        decrypted_secret_key = rsa_utils.decrypt_secret_key(card.aes_key.key)
        decrypted_iv = rsa_utils.decrypt_secret_key(card.aes_key.iv)
        card.card_number = rsa_utils.decrypt_aes_encryption(card.card_number, decrypted_secret_key, decrypted_iv)
        card.card_expire_month = rsa_utils.decrypt_aes_encryption(card.card_expire_month, decrypted_secret_key, decrypted_iv)
        card.card_expire_year = rsa_utils.decrypt_aes_encryption(card.card_expire_year, decrypted_secret_key, decrypted_iv)
        card.card_cvv = rsa_utils.decrypt_aes_encryption(card.card_cvv, decrypted_secret_key, decrypted_iv)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Decryption process Error")
    
    encrypted_card_number = crypto_utils.encrypt(card.card_number)
    encrypted_card_expire_month = crypto_utils.encrypt(card.card_expire_month)
    encrypted_card_expire_year = crypto_utils.encrypt(card.card_expire_year)
    encrypted_card_cvv = crypto_utils.encrypt(card.card_cvv)
    existing_encrypted_card_number = db.query(models.Card).filter(models.Card.user_id == cas_user_id, models.Card.card_number == encrypted_card_number).first()
    if existing_encrypted_card_number:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Card already registed in this user")

    card_details = {
        "user_id": cas_user_id,
        "card_number": encrypted_card_number,
        "card_expire_month": encrypted_card_expire_month,
        "card_expire_year": encrypted_card_expire_year,
        "card_cvv": encrypted_card_cvv,
    }

    db_card = models.Card(**card_details)
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    db_card.card_number = crypto_utils.decrypt(db_card.card_number)
    return db_card

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_card(card_id: int, db: Session = Depends(get_db), cas_user = Depends(cas.cas_service_ticket_validator)):
    
    cas_user_id = cas_user['user_id']
    card = db.query(models.Card).filter(models.Card.card_id == card_id).first()
    if(not card):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    if(card.user_id != cas_user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to delete this card")

    db.delete(card)
    db.commit()
    return {"message": "Card deleted successfully"}

