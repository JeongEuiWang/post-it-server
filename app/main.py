from fastapi import FastAPI
from app.core.database import init_database
from app.modules.auth.routes import auth_router

app = FastAPI()
app.include_router(auth_router, prefix="/auth", tags=["auth"])


@app.on_event("startup")
def start_up():
    init_database()
