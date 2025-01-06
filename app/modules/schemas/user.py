from pydantic import BaseModel


class LoginResponse(BaseModel):
    email: str
    id: int
    google_id: str
