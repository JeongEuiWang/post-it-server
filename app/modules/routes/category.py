from fastapi import APIRouter, HTTPException, Depends, Path, Query, Header
from app.modules.models import User, Category
from fastapi.responses import JSONResponse
from app.modules.service import (verify_google_oauth, create_gmail_service, verify_google_access)
from app.core.database import get_db
from app.modules.schemas import (BaseCategorySchema,
                                 CreateCategoryRequest,
                                 CreateCategoryResponse,
                                 UpdateCategoryRequest,
                                 UpdateCategoryResponse,
                                 DeleteCategoryRequest,
                                 DeleteCategoryResponse)
from sqlalchemy.orm import Session
from dateutil import parser
from datetime import datetime, timezone, timedelta
import pandas as pd

router = APIRouter()


@router.post('', response_model=CreateCategoryResponse)
async def create_category(
        request: CreateCategoryRequest,
        db: Session = Depends(get_db)
):
    print(request)
    # 1. 유저 존재 여부 확인
    user = db.query(User).filter(User.id.is_(request.userId)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User does not exist")

    # 2. 카테고리 중복 여부 확인 (이름 및 이메일 모두 Unique value)
    existing_category_name = db.query(Category).filter(
        Category.name.is_(request.name), Category.user_id.is_(request.userId)
    ).first()

    if existing_category_name:
        raise HTTPException(status_code=400, detail="Category already exists")

    existing_category_email = db.query(Category).filter(
        Category.from_email.is_(request.fromEmail), Category.user_id.is_(request.userId)
    ).first()

    if existing_category_email:
        raise HTTPException(status_code=400, detail="Email already exists")

    new_category = Category(
        name=request.name,
        user_id=request.userId,
        from_email=request.fromEmail
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    created_category = db.query(Category).filter(
        Category.name.is_(request.name),
        Category.from_email.is_(request.fromEmail),
    ).first()

    return CreateCategoryResponse(
        id=created_category.id,
        name=created_category.name,
        user_id=created_category.user_id,
        from_email=created_category.from_email
    )


@router.put('/{category_id}', response_model=UpdateCategoryResponse)
async def update_category(
        request: UpdateCategoryRequest,
        category_id: int = Path(..., title="카테고리 ID"),
        db: Session = Depends(get_db)
):
    # 1. 카테고리 존재 여부 확인
    category = db.query(Category).filter(Category.id.is_(category_id)).first()
    if not category:
        raise HTTPException(status_code=404, detail="카테고리가 존재하지 않습니다.")

    # 2. 유저 존재 여부 확인
    user = db.query(User).filter(User.id.is_(request.userId)).first()
    if not user:
        raise HTTPException(status_code=404, detail="존재하지 않는 유저입니다.")

    # 3-a. 이름 변경 요청
    if request.name:
        print("Enter condition name")
        new_name = request.name
        existing_category_name = db.query(Category).filter(
            Category.name.is_(new_name),
            Category.user_id.is_(request.userId),
            Category.id.is_not(category_id)
        ).first()
        print(existing_category_name)
        if existing_category_name:
            raise HTTPException(status_code=400, detail="이미 존재하는 이름입니다.")
        category.name = new_name

    # 3-b. 이메일 변경 요청
    if request.fromEmail:
        new_email = request.fromEmail
        existing_category_email = db.query(Category).filter(
            Category.from_email.is_(new_email),
            Category.user_id.is_(request.userId),
            Category.id.is_not(category_id)
        ).first()
        if existing_category_email:
            raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")
        category.from_email = new_email
    db.commit()
    db.refresh(category)

    updated_category = db.query(Category).filter(Category.id.is_(category_id)).first()

    return UpdateCategoryResponse(
        id=updated_category.id,
        name=updated_category.name,
        user_id=updated_category.user_id,
        from_email=updated_category.from_email
    )


@router.delete('/{category_id}', response_model=DeleteCategoryResponse)
async def delete_category(
        request: DeleteCategoryRequest,
        category_id: int = Path(..., title="카테고리 ID"),
        db: Session = Depends(get_db)
):
    # 1. 카테고리 존재 여부 확인
    category = db.query(Category).filter(Category.id.is_(category_id)).first()
    if not category:
        raise HTTPException(status_code=404, detail="카테고리가 존재하지 않습니다.")

    # 2. 유저 일치 여부 확인
    if category.user_id != request.userId:
        raise HTTPException(status_code=404, detail="일치하는 사용자가 아닙니다.")
    db.delete(category)
    db.commit()

    return DeleteCategoryResponse(
        success=True,
    )


@router.get('/categories', response_model=list[BaseCategorySchema])
async def get_categories(
        user_id: int = Query(..., alias="userId", title="요청 사용자"),
        db: Session = Depends(get_db)
):
    # 1. 카테고리 존재 여부 확인
    categories = db.query(Category).filter(Category.user_id.is_(user_id)).all()

    return categories
