from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from app.config import settings
from app.database import get_db
from app.models import User
from app.schemas import Token, UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserCreate)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return user_data


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect credentials")

    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value}
    )

    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=1800,
        samesite="lax",
        secure=False,
        path="/",
    )
    return response


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Проверка токена и получение текущего пользователя"""
    return current_user


@router.post("/logout")
async def logout():
    response = RedirectResponse(url="/login")
    response.delete_cookie(key="access_token")
    return response
