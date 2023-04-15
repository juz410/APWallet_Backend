from ..utils import hash_utils, otp_utils
from .. import models, schemas, cas
from fastapi import HTTPException, Response, status, Depends, APIRouter
from ..database import get_db
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter( 
    prefix='/auth',
    tags=['Authentication'])

@router.post('/validate_pin_number', status_code=status.HTTP_200_OK)
def validate_pin_number(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == user_credentials.username).first()
    if(not user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if(not hash_utils.verify(user_credentials.password, user.pin_number)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Pin Number")

    return Response(status_code=status.HTTP_200_OK)

@router.post('/change_pin', status_code=status.HTTP_200_OK)
def change_pin(change_pin_request: schemas.ChangePinRequest ,db: Session = Depends(get_db), cas_user = Depends(cas.cas_service_ticket_validator)):
    user_id = cas_user['user_id']
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if not otp_utils.verify_otp(user.email, change_pin_request.otp):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid OTP")
    if len(change_pin_request.new_pin) != 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Pin number must be 6 digits")

    user.pin_number = hash_utils.hash(change_pin_request.new_pin)
    db.commit()
    return {"message": "Pin number changed successfully"}