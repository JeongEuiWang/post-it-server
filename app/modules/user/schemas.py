from pydantic import BaseModel, Field


class UserBase(BaseModel):
    email: str = Field(..., description="유저의 gmail")
    id: int = Field(..., description="유저의 ID")
    google_id: str = Field(..., description="유저의 Google ID")


class LoginRequest(BaseModel):
    id_token: str = Field(..., alias="idToken", description="Google ID Token")


class LoginResponse(UserBase):
    pass

    class Config:
        from_attributes = True
