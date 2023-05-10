from fastapi import FastAPI, Depends
from . import models, cas
from .database import engine
from .routers import user, auth, card, transaction, otp, key
import json
from fastapi.middleware.cors import CORSMiddleware
from .utils import crypto_utils, rsa_utils
import base64
from pydantic import BaseModel

class EncryptedData(BaseModel):
    encryptedData: str
    iv: str
    secretKey: str




models.Base.metadata.create_all(bind=engine)


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(card.router)
app.include_router(transaction.router)
app.include_router(otp.router)
app.include_router(key.router)


@app.get("/")
def root():
    return {"message": "Hello World"}
