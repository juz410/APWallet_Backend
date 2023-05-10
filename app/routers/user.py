from ..utils import hash_utils, rsa_utils
from .. import models, schemas, cas
from fastapi import HTTPException, status, Depends, APIRouter
from ..database import get_db
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/user",
    tags=["user"],
)

@router.get("/", response_model=schemas.UserOut)
def get_user(db: Session = Depends(get_db), cas_user = Depends(cas.cas_service_ticket_validator)):
    cas_user_id = cas_user['user_id']
    user = db.query(models.User).filter(models.User.user_id == cas_user_id).first()
    if(not user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.role = cas_user['role']
    return user

@router.get("/search")
def search_user(user_id: str, db: Session = Depends(get_db), cas_user = Depends(cas.cas_service_ticket_validator)):
    print(user_id)
    receiver = db.query(models.User).filter(models.User.user_id == user_id).first()
    print(receiver)
    if(not receiver):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return receiver

@router.post("/register", response_model=schemas.UserOut, description="Note: User's PIN Number must be encrypted")
def register_new_user( user_register: schemas.UserRegister, db: Session = Depends(get_db), cas_user = Depends(cas.cas_service_ticket_validator)):
    cas_user_id = cas_user['user_id']
    try:
        decrypted_secret_key = rsa_utils.decrypt_secret_key(user_register.aes_key.key)
        decrypted_iv = rsa_utils.decrypt_secret_key(user_register.aes_key.iv)
        user_register.pin_number = rsa_utils.decrypt_aes_encryption(user_register.pin_number, decrypted_secret_key, decrypted_iv)
    except Exception as e:
        print(f"Error decrypting pin number: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error decrypting data")    
    existing_user = db.query(models.User).filter(models.User.user_id == cas_user_id).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    
    existing_phone_number = db.query(models.User).filter(models.User.phone_number == user_register.phone_number).first()
    if existing_phone_number:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number already exists")
    
    if len(user_register.pin_number) != 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Pin number must be 6 digits")

    user: schemas.UserClass = {
        "user_id": cas_user_id,
        "email": cas_user['email'],
        "name": cas_user['name'],
        "phone_number": user_register.phone_number,
        "balance": 0,
        "pin_number": hash_utils.hash(user_register.pin_number),
    }

    db_user = models.User(**user)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db_user.role = cas_user['role']
    return db_user

    