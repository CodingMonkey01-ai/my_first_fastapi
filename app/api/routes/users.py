import json
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models
from db.redis import redis_client
from db.session import SessionLocal
from schemas import User, UserCreate

router = APIRouter()
USERS_CACHE_KEY = "users:all"
USERS_CACHE_TTL_SECONDS = 60


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/users", response_model=User, status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    user = models.User(name=payload.name, email=payload.email)
    db.add(user)
    db.commit()
    db.refresh(user)
    redis_client.delete(USERS_CACHE_KEY)
    return user


@router.get("/users", response_model=List[User])
def get_users(db: Session = Depends(get_db)):
    cached_users = redis_client.get(USERS_CACHE_KEY)
    if cached_users:
        return json.loads(cached_users)

    users = db.query(models.User).all()
    serialized_users = [
        {"id": user.id, "name": user.name, "email": user.email}
        for user in users
    ]
    redis_client.setex(
        USERS_CACHE_KEY,
        USERS_CACHE_TTL_SECONDS,
        json.dumps(serialized_users),
    )
    return users
