from pydantic import BaseModel, Field, model_validator
from typing import Optional


class BaseCategory(BaseModel):
    id: int = Field(..., description="카테고리의 ID")
    user_id: int = Field(..., description="카테고리의 User ID")
    name: str = Field(..., description="카테고리의 이름")
    from_email: str = Field(..., description="카테고리의 From Email")

    class Config:
        from_attributes = True


class CreateCategoryRequest(BaseModel):
    user_id: int = Field(..., alias="userId", description="요청 사용자의 ID")
    name: str = Field(..., description="라벨로 표시될 카테고리의 이름")
    from_email: str = Field(..., alias="fromEmail", description="Gmail 필터링을 위한 수신자 이메일 주소")


class CreateCategoryResponse(BaseCategory):
    pass

    class Config:
        from_attributes = True


class UpdateCategoryRequest(BaseModel):
    user_id: int = Field(..., alias="userId", description="요청 사용자의 ID", )
    name: Optional[str] = Field(None, description="수정할 카테고리의 이름")
    from_email: Optional[str] = Field(None, alias="fromEmail", description="수정할 수신자 이메일 주소")

    @model_validator(mode="before")
    @classmethod
    def validate_is_empty(cls, data):
        name = data.get("name")
        from_email = data.get("fromEmail")
        if not name and not from_email:
            raise ValueError("이메일이나 이름중 한가지는 입력되어야 합니다.")
        return data


class UpdateCategoryResponse(BaseCategory):
    pass

    class Config:
        from_attributes = True


class DeleteCategoryRequest(BaseModel):
    userId: int = Field(..., description="요청 사용자의 ID")


class DeleteCategoryResponse(BaseModel):
    success: bool = True
