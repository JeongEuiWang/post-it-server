from fastapi import FastAPI
from app.core.database import init_database
from app.modules.user.routes import router as user_router
from app.modules.category.routes import router as category_router
from app.modules.article.routes import router as article_router

app = FastAPI()
app.include_router(user_router, prefix="/user", tags=["user"])
app.include_router(category_router, prefix="/category", tags=["category"])
app.include_router(article_router, prefix="/article", tags=["article"])


@app.on_event("startup")
def start_up():
    init_database()
