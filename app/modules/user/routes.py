from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.user.schemas import LoginResponse, LoginRequest
from app.modules.user.service import get_user_by_email, create_user
from app.utils.google_auth import verify_google_oauth

router = APIRouter()


@router.post('/login', response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    # id_token = request.get("idToken")
    #
    # if not id_token:
    #     raise HTTPException(status_code=400, detail="Missing id_token")
    try:
        user_info = verify_google_oauth(id_token=request.id_token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

    user = get_user_by_email(db=db, email=user_info.get("email"))
    if not user:
        new_user = create_user(db=db, google_id=user_info["user_id"], email=user_info["email"])
        return LoginResponse.from_orm(new_user)
    return LoginResponse.from_orm(user)
