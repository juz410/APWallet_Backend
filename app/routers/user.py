from ..utils import hash_utils
from .. import models, schemas, cas
from fastapi import HTTPException, status, Depends, APIRouter
from ..database import get_db
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/user",
    tags=["user"],
)

@router.get("/", response_model=schemas.User)
def get_user(db: Session = Depends(get_db), cas_user = Depends(cas.cas_service_ticket_validator)):
    cas_user_id = cas_user['user_id']
    user = db.query(models.User).filter(models.User.user_id == cas_user_id).first()
    if(not user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.post("/register", response_model=schemas.User)
def register_new_user( user_register: schemas.UserRegister, db: Session = Depends(get_db), cas_user = Depends(cas.cas_service_ticket_validator)):
    cas_user_id = cas_user['user_id']
    existing_user = db.query(models.User).filter(models.User.user_id == cas_user_id).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    
    existing_phone_number = db.query(models.User).filter(models.User.phone_number == user_register.phone_number).first()
    if existing_phone_number:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number already exists")
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
    return db_user

    