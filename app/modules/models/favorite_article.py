from sqlalchemy import Column, Integer, String, ForeignKey
from app.core.database import Base


class FavoriteArticle(Base):
    __tablename__ = "favorite_article"
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(String, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), index=True)
    category_id = Column(Integer, ForeignKey("category.id"), index=True)