from pydantic import BaseModel, Field, model_validator, ValidationError
from typing import Optional


class BaseCategorySchema(BaseModel):
    id: int = Field(..., title="카테고리의 ID")
    user_id: int = Field(..., title="카테고리의 User ID")
    name: str = Field(..., title="카테고리의 이름")
    from_email: str = Field(..., title="카테고리의 From Email")


class CreateCategoryRequest(BaseModel):
    userId: int = Field(..., title="요청 사용자의 ID")
    name: str = Field(..., title="라벨로 표시될 카테고리의 이름")
    fromEmail: str = Field(..., title="Gmail 필터링을 위한 수신자 이메일 주소")


class CreateCategoryResponse(BaseCategorySchema):
    pass


class UpdateCategoryRequest(BaseModel):
    userId: int = Field(..., title="요청 사용자의 ID", )
    name: Optional[str] = Field(None, title="수정할 카테고리의 이름")
    fromEmail: Optional[str] = Field(None, title="수정할 수신자 이메일 주소")

    @model_validator(mode="before")
    @classmethod
    def validate_is_empty(cls, data):
        name = data.get("name")
        from_email = data.get("fromEmail")
        if not name and not from_email:
            raise ValueError("이메일이나 이름중 한가지는 입력되어야 합니다.")
        return data


class UpdateCategoryResponse(BaseCategorySchema):
    pass


class DeleteCategoryRequest(BaseModel):
    userId: int = Field(..., title="요청 사용자의 ID")


class DeleteCategoryResponse(BaseModel):
    success: bool = True


class GetCategoriesRequest(BaseModel):
    userId: int = Field(..., title="요청 사용자의 ID")


class GetCategoriesResponse(BaseModel):
    categories: list[BaseCategorySchema] = Field(..., title="카테고리 목록")
