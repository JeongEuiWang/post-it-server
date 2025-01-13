from fastapi import APIRouter, HTTPException, Depends, Path, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.category.schemas import (BaseCategory,
                                          CreateCategoryRequest,
                                          CreateCategoryResponse,
                                          UpdateCategoryRequest,
                                          UpdateCategoryResponse,
                                          DeleteCategoryRequest,
                                          DeleteCategoryResponse)
from app.modules.category.service import (get_category_by_id,
                                          get_category_by_name,
                                          get_category_by_from_email,
                                          create_category,
                                          update_category,
                                          get_categories_by_user_id)
from app.modules.user.service import get_user_by_id

router = APIRouter()


@router.post('', response_model=CreateCategoryResponse)
async def create_category_api(
        request: CreateCategoryRequest,
        db: Session = Depends(get_db)
):
    user = get_user_by_id(db=db, user_id=request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="존재하지 않는 사용자입니다.")

    existing_name_category = get_category_by_name(db=db, name=request.name, user_id=request.user_id)

    if existing_name_category:
        raise HTTPException(status_code=400, detail="이미 존재하는 카테고리 이름입니다.")

    existing_email_category = get_category_by_from_email(db=db, from_email=request.from_email, user_id=request.user_id)

    if existing_email_category:
        raise HTTPException(status_code=400, detail="이미 존재하는 카테고리 이메일입니다.")

    create_category(db=db, request=request)

    created_category = get_category_by_from_email(db=db, from_email=request.from_email, user_id=request.user_id)

    return CreateCategoryResponse.from_orm(created_category)


@router.put('/{category_id}', response_model=UpdateCategoryResponse)
async def update_category_api(
        request: UpdateCategoryRequest,
        category_id: int = Path(..., description="카테고리 ID"),
        db: Session = Depends(get_db)
):
    user = get_user_by_id(db=db, user_id=request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="존재하지 않는 사용자입니다.")
    category = get_category_by_id(db, category_id)

    if not category:
        raise HTTPException(status_code=404, detail="카테고리가 존재하지 않습니다.")

    if request.name:
        existing_name_category = get_category_by_name(db=db, name=request.name, user_id=request.user_id)
        if existing_name_category:
            raise HTTPException(status_code=400, detail=f"이미 존재하는 이름입니다.")
        category.name = request.name

    if request.from_email:
        existing_email_category = get_category_by_from_email(db=db, from_email=request.from_email,
                                                             user_id=request.user_id)
        if existing_email_category:
            raise HTTPException(status_code=400, detail=f"이미 존재하는 이메일입니다.")
        category.from_email = request.from_email

    update_category(db=db, category=category)
    updated_category = get_category_by_id(db=db, category_id=category_id)

    return UpdateCategoryResponse.from_orm(updated_category)


@router.delete('/{category_id}', response_model=DeleteCategoryResponse)
async def delete_category(
        request: DeleteCategoryRequest,
        category_id: int = Path(..., description="카테고리 ID"),
        db: Session = Depends(get_db)
):
    category = get_category_by_id(db=db, category_id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="카테고리가 존재하지 않습니다.")

    if category.user_id != request.userId:
        raise HTTPException(status_code=404, detail="일치하는 사용자가 아닙니다.")
    db.delete(category)
    db.commit()

    return DeleteCategoryResponse(
        success=True
    )


@router.get('/categories', response_model=list[BaseCategory])
async def get_categories(
        user_id: int = Query(..., alias="userId", title="요청 사용자"),
        db: Session = Depends(get_db)
):
    categories = get_categories_by_user_id(db=db, user_id=user_id)
    return categories
