from fastapi import APIRouter
from ..config import settings

router = APIRouter(
    prefix='/key',
    tags=['Key']
  )

@router.get("/public-key")
async def get_public_key():
    public_key = settings.public_key

    if not public_key:
        return {"error": "Public key not found."}

    return {"public_key": public_key}
