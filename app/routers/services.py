from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Service
from app.schemas import ServiceBase, ServiceResponse
from app.dependencies import get_manager_or_admin

router = APIRouter(prefix="/services", tags=["Services"])

@router.get("/", response_model=list[ServiceResponse])
async def get_services(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Service).where(Service.is_active == True))
    return result.scalars().all()

@router.post("/", response_model=ServiceResponse, dependencies=[Depends(get_manager_or_admin)])
async def create_service(service: ServiceBase, db: AsyncSession = Depends(get_db)):
    new_service = Service(**service.model_dump())
    db.add(new_service)
    await db.commit()
    await db.refresh(new_service)
    return new_service

@router.delete("/{service_id}", dependencies=[Depends(get_manager_or_admin)])
async def delete_service(service_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    service.is_active = False 
    await db.commit()
    return {"message": "Service deleted"}
