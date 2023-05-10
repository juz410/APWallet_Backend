from ..utils import hash_utils, otp_utils,rsa_utils
from .. import models, schemas, cas
from fastapi import HTTPException, Response, status, Depends, APIRouter
from ..database import get_db
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter( 
    prefix='/auth',
    tags=['Authentication'])

@router.post('/validate_pin_number', status_code=status.HTTP_200_OK, description="Note: User's PIN Number must be encrypted")
def validate_pin_number(validatePin: schemas.validatePin, db: Session = Depends(get_db), cas_user = Depends(cas.cas_service_ticket_validator)):
    user_id = cas_user['user_id']
    try:
        decrypted_secret_key = rsa_utils.decrypt_secret_key(validatePin.aes_key.key)
        decrypted_iv = rsa_utils.decrypt_secret_key(validatePin.aes_key.iv)
        validatePin.pin_number = rsa_utils.decrypt_aes_encryption(validatePin.pin_number, decrypted_secret_key, decrypted_iv)
    except Exception as e:
        print(f"Error decrypting pin number: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error decrypting pin number")

    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if(not user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if(not hash_utils.verify(validatePin.pin_number, user.pin_number)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid pin number")

    return "Pin number validated successfully"

@router.post('/change_pin', status_code=status.HTTP_200_OK, description="Note: User's PIN Number must be encrypted")
def change_pin(change_pin_request: schemas.ChangePinRequest ,db: Session = Depends(get_db), cas_user = Depends(cas.cas_service_ticket_validator)):
    try:
        decrypted_secret_key = rsa_utils.decrypt_secret_key(change_pin_request.aes_key.key)
        decrypted_iv = rsa_utils.decrypt_secret_key(change_pin_request.aes_key.iv)
        change_pin_request.new_pin = rsa_utils.decrypt_aes_encryption(change_pin_request.new_pin, decrypted_secret_key, decrypted_iv)
    except Exception as e:
        print(f"Error decrypting pin number: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error decrypting data")    
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

#To be decided to implement backend to frontend encryption or not
# @router.post('/store-public-key')
# def store_public_key(public_key: schemas.PublicKey):
#     try:
#         with open("public_key.pem", "w") as f:
#             f.write(public_key.publicKey)
#         return {"message": "Public key stored successfully"}
#     except Exception as e:
#         print(f"Error writing public key to file: {e}")
#         return {"error": "Error writing public key to file"}