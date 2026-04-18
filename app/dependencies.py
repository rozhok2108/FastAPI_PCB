from fastapi import Depends, HTTPException, status
from app.models import User, UserRole
from app.auth import get_current_user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    return current_user

async def get_manager_or_admin(current_user: User = Depends(get_current_active_user)):
    if current_user.role not in [UserRole.MANAGER, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

async def get_admin(current_user: User = Depends(get_current_active_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

async def get_engineer_or_manager(current_user: User = Depends(get_current_active_user)):
    if current_user.role not in [UserRole.ENGINEER, UserRole.MANAGER, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

async def get_engineer(current_user: User = Depends(get_current_active_user)):
    if current_user.role not in [UserRole.ENGINEER, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Engineer access required")
    return current_user