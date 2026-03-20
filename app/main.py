import time

from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from fastapi import FastAPI

from api.routes.users import router as users_router
from db.redis import redis_client
from db.session import Base, engine

app = FastAPI()

app.include_router(users_router)


def wait_for_database(max_attempts: int = 10, delay_seconds: int = 2) -> None:
    for attempt in range(1, max_attempts + 1):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            Base.metadata.create_all(bind=engine)
            return
        except OperationalError:
            if attempt == max_attempts:
                raise
            time.sleep(delay_seconds)


@app.on_event("startup")
def startup() -> None:
    wait_for_database()


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
