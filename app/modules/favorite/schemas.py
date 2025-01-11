from pydantic import BaseModel, Field


class FavoriteBase(BaseModel):
    id: int = Field(..., description="The id of the favorite")
    user_id: int = Field(..., description="The user id of the favorite")
    category_id: int = Field(..., description="The category id of the favorite")
    message_id: str = Field(..., description="The message id of the favorite")


class CreateFavoriteRequest(BaseModel):
    user_id: int = Field(..., alias="userId", description="The user id of the favorite")
    category_id: int = Field(..., alias="categoryId", description="The category id of the favorite")
    message_id: str = Field(..., alias="messageId", description="The message id of the favorite")

    class Config:
        from_attributes = True


class CreateFavoriteResponse(FavoriteBase):
    pass

    class Config:
        from_attributes = True


class CheckIsFavoriteResponse(BaseModel):
    is_favorite: bool


class DeleteFavoriteResponse(BaseModel):
    success: bool
