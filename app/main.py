from fastapi import FastAPI, Depends
from . import models, cas
from .database import engine
from .routers import user, auth, card, transaction
import json



models.Base.metadata.create_all(bind=engine)


app = FastAPI()

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(card.router)
app.include_router(transaction.router)


@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/test")
def test_cas(cas_response = Depends(cas.cas_service_ticket_validator)):
    return json.loads(cas_response)
    