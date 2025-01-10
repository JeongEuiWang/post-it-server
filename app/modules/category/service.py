from sqlalchemy.orm import Session
from app.modules.category.models import Category
from app.modules.category.schemas import CreateCategoryRequest


def get_categories_by_user_id(db: Session, user_id: int):
    return db.query(Category).filter(Category.user_id.is_(user_id)).all()


def get_category_by_id(db: Session, category_id: int) -> Category | None:
    return db.query(Category).filter(Category.id.is_(category_id)).first()


def get_category_by_name(db: Session, name: str, user_id: int):
    return db.query(Category).filter(
        Category.name.is_(name), Category.user_id.is_(user_id)

    ).first()


def get_category_by_from_email(db: Session, from_email: str, user_id: int):
    return db.query(Category).filter(
        Category.from_email.is_(from_email), Category.user_id.is_(user_id)
    ).first()


def create_category(db: Session, request: CreateCategoryRequest):
    category = Category(
        name=request.name,
        user_id=request.user_id,
        from_email=request.from_email
    )

    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(db: Session, category: Category):
    db.commit()
    db.refresh(category)
    return category
