from fastapi import APIRouter, HTTPException, Depends, Query, Header, Path
from fastapi.responses import JSONResponse
from app.modules.category.models import Category
from app.utils.gmail import create_gmail_service
from app.utils.google_auth import verify_google_access
from app.modules.article.service import parse_base_message_service
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.utils.validate_header import validate_header
from app.modules.user.models import User

router = APIRouter()


@router.get('')
async def get_article_list(
        category_id: int = Query(..., alias="categoryId", title="카테고리 ID"),
        user_id: int = Query(..., alias="userId", title="요청 사용자"),
        authorization: str = Header(None),
        db: Session = Depends(get_db)
):
    try:
        validate_header(authorization)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

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
    # 전체 메일 조회
    results = gmail_service.users().messages().list(userId=request_user.google_id, q=query).execute()
    messages = results["messages"]
    message_detail_list = []
    for message in messages:
        message_detail = gmail_service.users().messages().get(userId=request_user.google_id, id=message["id"]).execute()
        if "html" not in message_detail["payload"]["mimeType"]:
            continue
        else:
            payload = parse_base_message_service(message_detail)
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
    try:
        validate_header(authorization)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

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
    payload = parse_base_message_service(message_detail)
    content = message_detail["payload"]["body"]["data"]
    message_detail_payload = {
        **payload,
        "category_name": category.name,
        "content": content
    }

    return JSONResponse(content=message_detail_payload, status_code=200)
