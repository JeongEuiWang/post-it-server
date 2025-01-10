from sqlalchemy.orm import Session

from app.modules.user.models import User


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email.is_(email)).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id.is_(user_id)).first()


def create_user(db: Session, google_id: str, email: str) -> User:
    user = User(
        google_id=google_id,
        email=email,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
