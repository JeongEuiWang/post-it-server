from sqlalchemy import Column, Integer, String, ForeignKey
from app.core.database import Base


class Favorite(Base):
    __tablename__ = "favorite"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("category.id", ondelete="CASCADE"), nullable=False)
    message_id = Column(String, nullable=False)
