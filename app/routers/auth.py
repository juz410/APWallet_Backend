from ..utils import hash_utils
from .. import models, schemas
from fastapi import HTTPException, Response, status, Depends, APIRouter
from ..database import get_db
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(tags=['Authentication'])

@router.post('/validate_pin_number', status_code=status.HTTP_200_OK)
def validate_pin_number(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == user_credentials.username).first()
    if(not user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if(not hash_utils.verify(user_credentials.password, user.pin_number)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Pin Number")

    return Response(status_code=status.HTTP_200_OK)

    
    