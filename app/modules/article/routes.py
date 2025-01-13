from fastapi import APIRouter, HTTPException, Depends, Query, Header, Path
from fastapi.responses import JSONResponse
from app.utils.gmail import create_gmail_service
from app.utils.google_auth import verify_google_access
from app.modules.article.service import parse_base_message_service, find_message_content_html
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.utils.validate_header import validate_header
from app.modules.user.service import get_user_by_id
from app.modules.category.service import get_category_by_id

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

    request_user = get_user_by_id(db=db, user_id=user_id)

    if not request_user:
        raise HTTPException(status_code=404, detail="User not found")

    if request_user.email != google_auth.get("email"):
        raise HTTPException(status_code=401, detail="Authorization Failed")

    gmail_service = create_gmail_service(token)
    category = get_category_by_id(db=db, category_id=category_id)

    query = f"from:{category.from_email}" if category.from_email else ""
    # 전체 메일 조회
    results = gmail_service.users().messages().list(userId=request_user.google_id, q=query, maxResults=20).execute()
    messages = results["messages"]
    message_detail_list = []
    for message in messages:
        message_detail = gmail_service.users().messages().get(userId=request_user.google_id, id=message["id"]).execute()
        payload = {
            **parse_base_message_service(message_detail),
            "message_id": message["id"]
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
    try:
        validate_header(authorization)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

    token = authorization[len("Bearer "):]  # "Bearer " 제거하여 토큰 추출

    google_auth = verify_google_access(token)

    request_user = get_user_by_id(db=db, user_id=user_id)

    if not request_user:
        raise HTTPException(status_code=404, detail="User not found")

    if request_user.email != google_auth.get("email"):
        raise HTTPException(status_code=401, detail="Authorization Failed")

    gmail_service = create_gmail_service(token)
    category = get_category_by_id(db=db, category_id=category_id)

    message_detail = gmail_service.users().messages().get(userId=request_user.google_id, id=message_id).execute()
    payload = parse_base_message_service(message_detail)
    content = find_message_content_html(message_detail["payload"])
    message_detail_payload = {
        **payload,
        "category_name": category.name,
        "content": content
    }

    print(message_detail_payload)

    return JSONResponse(content=message_detail_payload, status_code=200)
