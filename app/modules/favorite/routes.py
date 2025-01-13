from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.favorite.schemas import (CreateFavoriteRequest,
                                          CreateFavoriteResponse,
                                          CheckIsFavoriteResponse,
                                          DeleteFavoriteResponse)
from app.modules.favorite.service import get_favorite_by_message_id, create_favorite, delete_favorite
from app.modules.user.service import get_user_by_id
from app.modules.category.service import get_category_by_id

router = APIRouter()


@router.post('', response_model=CreateFavoriteResponse)
async def crate_favorite_api(request: CreateFavoriteRequest, db: Session = Depends(get_db)):
    print(request)
    request_user = get_user_by_id(db=db, user_id=request.user_id)

    if not request_user:
        raise HTTPException(status_code=404, detail="User not found")

    category = get_category_by_id(db=db, category_id=request.category_id)

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    if category.user_id != request.user_id:
        raise HTTPException(status_code=403, detail="User Missmatch")

    existing_message_id = get_favorite_by_message_id(db=db, message_id=request.message_id)

    if existing_message_id:
        raise HTTPException(status_code=400, detail="Favorite already exists")

    create_favorite(db=db, request=request)
    created_favorite = get_favorite_by_message_id(db=db, message_id=request.message_id)

    return CreateFavoriteResponse.from_orm(created_favorite)


@router.get('/check', response_model=CheckIsFavoriteResponse)
async def check_is_favorite_api(
        message_id: str = Query(..., alias="messageId", description="Message id"),
        db: Session = Depends(get_db)):
    favorite = get_favorite_by_message_id(db=db, message_id=message_id)

    return CheckIsFavoriteResponse(
        is_favorite=True if favorite else False,
    )


@router.delete('', response_model=DeleteFavoriteResponse)
async def delete_favorite_api(
        user_id: int = Query(..., alias="userId", description="User id"),
        message_id: str = Query(..., alias="messageId", description="Message id"),
        db: Session = Depends(get_db)
):
    favorite = get_favorite_by_message_id(db=db, message_id=message_id)

    if favorite.user_id != user_id:
        raise HTTPException(status_code=403, detail="User Missmatch")

    delete_favorite(db=db, favorite=favorite)

    return DeleteFavoriteResponse(
        success=True,
    )
