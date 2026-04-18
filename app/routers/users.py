from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User
from app.schemas import UserResponse
from app.dependencies import get_admin, get_manager_or_admin
from app.schemas import UserResponse, UserCreate, UserBase
from passlib.context import CryptContext

router = APIRouter(prefix="/users", tags=["Users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.get("/", response_model=list[UserResponse], dependencies=[Depends(get_manager_or_admin)])
async def get_all_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()

@router.delete("/{user_id}", dependencies=[Depends(get_admin)])
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await db.delete(user)
    await db.commit()
    return {"message": "User deleted"}

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_admin)])
async def create_user(
    user_data: UserCreate,  
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

  
    hashed_password = pwd_context.hash(user_data.password)

    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        role=user_data.role,  
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user

@router.patch("/{user_id}", response_model=UserResponse, dependencies=[Depends(get_admin)])
async def change_user(user_id: int, ch_user: UserBase, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    old_user = result.scalar_one_or_none()
    if ch_user.email and ch_user.email != old_user.email:
        email_check = await db.execute(select(User).where(User.email == ch_user.email))
        if email_check.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    old_user.email = ch_user.email
    old_user.role =ch_user.role
    await db.commit()
    await db.refresh(old_user)
    return old_user
