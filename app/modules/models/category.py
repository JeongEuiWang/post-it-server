from sqlalchemy import Column, Integer, String, ForeignKey
from app.core.database import Base


class Category(Base):
    __tablename__ = "category"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    from_email = Column(String, unique=True, nullable=False)