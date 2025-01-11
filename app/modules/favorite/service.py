from sqlalchemy.orm import Session
from app.modules.favorite.models import Favorite

from app.modules.favorite.schemas import CreateFavoriteRequest, FavoriteBase


def get_favorite_by_message_id(db: Session, message_id: str):
    return db.query(Favorite).filter(Favorite.message_id.is_(message_id)).first()


def create_favorite(db: Session, request: CreateFavoriteRequest) -> Favorite:
    favorite = Favorite(
        message_id=request.message_id,
        user_id=request.user_id,
        category_id=request.category_id
    )

    db.add(favorite)
    db.commit()
    db.refresh(favorite)

    return favorite


def delete_favorite(db: Session, favorite: FavoriteBase):
    db.delete(favorite)
    db.commit()
    return True
