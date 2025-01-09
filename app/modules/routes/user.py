from fastapi import APIRouter, HTTPException, Depends, Request
from app.modules.models import User
from app.core.database import get_db
from app.modules.schemas import LoginResponse
from app.modules.service import verify_google_oauth
from sqlalchemy.orm import Session

router = APIRouter()


@router.post('/login', response_model=LoginResponse)
async def google_login(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    id_token = data.get("idToken")

    if not id_token:
        raise HTTPException(status_code=400, detail="Missing id_token")

    user_info = verify_google_oauth(id_token)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid id_token")

    user = db.query(User).filter(User.email.is_(user_info.get("email"))).first()
    if not user:
        user = User(
            google_id=user_info["sub"],
            email=user_info["email"],
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return LoginResponse(email=user.email, google_id=user.google_id, id=user.id)
