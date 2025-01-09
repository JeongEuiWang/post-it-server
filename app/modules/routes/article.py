from fastapi import APIRouter, HTTPException, Depends, Query, Header, Path
from app.modules.models import User, Category
from fastapi.responses import JSONResponse
from app.modules.service import (create_gmail_service, verify_google_access)
from app.core.database import get_db
from sqlalchemy.orm import Session
import pandas as pd

router = APIRouter()


@router.get('')
async def get_article_list(
        category_id: int = Query(..., alias="categoryId", title="카테고리 ID"),
        user_id: int = Query(..., alias="userId", title="요청 사용자"),
        authorization: str = Header(None),
        db: Session = Depends(get_db)
):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")

    token = authorization[len("Bearer "):]  # "Bearer " 제거하여 토큰 추출

    google_auth = verify_google_access(token)

    request_user = db.query(User).filter(User.id.is_(user_id)).first()

    if not request_user:
        raise HTTPException(status_code=404, detail="User not found")

    if request_user.email != google_auth.get("email"):
        raise HTTPException(status_code=404, detail="Authorization Failed")

    gmail_service = create_gmail_service(token)
    category = db.query(Category).filter(Category.id.is_(category_id)).first()

    query = f"from:{category.from_email}" if category.from_email else ""
    results = gmail_service.users().messages().list(userId=request_user.google_id, q=query).execute()
    messages = results["messages"]
    message_detail_list = []
    for message in messages:
        message_detail = gmail_service.users().messages().get(userId=request_user.google_id, id=message["id"]).execute()
        if "html" not in message_detail["payload"]["mimeType"]:
            continue
        else:
            headers = message_detail["payload"]["headers"]
            date = message_detail["internalDate"]
            utc_date = pd.to_datetime(float(date), unit='ms', utc=True)
            kst_date = utc_date.tz_convert("Asia/Seoul").date()
            payload = {
                "title": next((header["value"] for header in headers if header.get("name") == "Subject"), "-"),
                "snippet": message_detail["snippet"] or "-",
                "date": kst_date.isoformat(),
                "message_id": message_detail["id"]
            }
            message_detail_list.append(payload)
    return JSONResponse(content=message_detail_list, status_code=200)

@router.get('/{message_id}')
async def get_article_detail(
        message_id: str = Path(..., title="message의 ID"),
        category_id: int = Query(..., alias="categoryId", title="카테고리 ID"),
        user_id: int = Query(..., alias="userId", title="요청 사용자"),
        authorization: str = Header(None),
        db: Session = Depends(get_db)
):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")

    token = authorization[len("Bearer "):]  # "Bearer " 제거하여 토큰 추출

    google_auth = verify_google_access(token)

    request_user = db.query(User).filter(User.id.is_(user_id)).first()

    if not request_user:
        raise HTTPException(status_code=404, detail="User not found")

    if request_user.email != google_auth.get("email"):
        raise HTTPException(status_code=404, detail="Authorization Failed")

    gmail_service = create_gmail_service(token)
    category = db.query(Category).filter(Category.id.is_(category_id)).first()

    message_detail = gmail_service.users().messages().get(userId=request_user.google_id, id=message_id).execute()
    headers = message_detail["payload"]["headers"]
    content = message_detail["payload"]["body"]["data"]

    date = message_detail["internalDate"]
    utc_date = pd.to_datetime(float(date), unit='ms', utc=True)
    kst_date = utc_date.tz_convert("Asia/Seoul").date()
    payload = {
        "category_name": category.name,
        "title": next((header["value"] for header in headers if header.get("name") == "Subject"), "-"),
        "snippet": message_detail["snippet"] or "-",
        "date": kst_date.isoformat(),
        "content": content
    }

    return JSONResponse(content=payload, status_code=200)
