from ..utils import crypto_utils, otp_utils, email_utils
from .. import models, schemas, cas
from fastapi import HTTPException, status, Depends, APIRouter
from ..database import get_db
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(
    prefix="/otp",
    tags=["otp"],
)

@router.post("/email")
async def send_otp_email(db: Session = Depends(get_db), cas_user = Depends(cas.cas_service_ticket_validator)):
    cas_user_id = cas_user['user_id']
    user = db.query(models.User).filter(models.User.user_id == cas_user_id).first()
    if(not user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user_email = user.email
    otp = otp_utils.generate_otp(user_email)
    
    await email_utils.send_email(
        to=[user_email],
        subject="Your OTP",
        body=f"Your One-Time Password is: {otp}\nIt will expire in 5 minutes."
    )
    return {"message": f"OTP sent to {user_email}.\n OTP is {otp}" }

