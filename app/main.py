from fastapi import FastAPI

from api.routes.users import router as users_router
from db.redis import redis_client
from db.session import Base, engine

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(users_router)


@app.get("/")
def root():
    return {"message": "API is working"}


@app.get("/health")
def health_check():
    redis_status = "connected"
    try:
        redis_client.ping()
    except Exception:
        redis_status = "disconnected"

    return {
        "api": "ok",
        "database": "configured",
        "redis": redis_status,
    }
