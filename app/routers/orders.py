from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models import Order, User, Service, OrderStatus, UserRole
from app.schemas import OrderCreate, OrderResponse, OrderStatusUpdate, OrderAssign
from app.dependencies import get_current_active_user, get_manager_or_admin, get_engineer
from app.utils.notifications import send_order_status_notification
from app.utils.logic import validate_status_transition
from datetime import datetime

router = APIRouter(prefix="/orders", tags=["Orders"])

def order_to_response(order: Order) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        client_id=order.client_id,
        engineer_id=order.engineer_id,
        description=order.description,
        status=order.status,
        created_at=order.created_at,
        service_ids=[s.id for s in order.services]
    )

@router.post("/", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(select(Service).where(Service.id.in_(order_data.service_ids)))
    services = result.scalars().all()
    if len(services) != len(order_data.service_ids):
        raise HTTPException(status_code=400, detail="Some services not found")

    client_id = order_data.client_id if (current_user.role == UserRole.ADMIN and order_data.client_id) else current_user.id

    new_order = Order(
        client_id=client_id,
        description=order_data.description,
        services=services
    )
    db.add(new_order)
    await db.commit()
    await db.refresh(new_order, attribute_names=['services'])
    return order_to_response(new_order)

@router.get("/my", response_model=list[OrderResponse])
async def get_my_orders(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    result = await db.execute(select(Order).options(selectinload(Order.services)).where(Order.client_id == current_user.id))
    orders = result.scalars().all()
    return [order_to_response(order) for order in orders]

@router.get("/engineer/assigned", response_model=list[OrderResponse])
async def get_assigned_orders(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_engineer)):
    """Получить заказы, назначенные инженеру"""
    result = await db.execute(select(Order).options(selectinload(Order.services)).where(Order.engineer_id == current_user.id))
    orders = result.scalars().all()
    return [order_to_response(order) for order in orders]

@router.get("/", response_model=list[OrderResponse], dependencies=[Depends(get_manager_or_admin)])
async def get_all_orders(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Order).options(selectinload(Order.services)))
    orders = result.scalars().all()
    return [order_to_response(order) for order in orders]

@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(order_id: int, status_data: OrderStatusUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.services), selectinload(Order.client))
        .where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

   
    if current_user.role == UserRole.ENGINEER and order.engineer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not assigned to this order")

    if not validate_status_transition(order.status, status_data.status):
        raise HTTPException(status_code=400, detail=f"Cannot transition from {order.status} to {status_data.status}")

    order.status = status_data.status
    await db.commit()

    await send_order_status_notification(order.client.email, order.status.value)

    return order_to_response(order)

@router.patch("/{order_id}/assign", response_model=OrderResponse, dependencies=[Depends(get_manager_or_admin)])
async def assign_engineer(order_id: int, assign_data: OrderAssign, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Order).options(selectinload(Order.services)).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    engineer_result = await db.execute(select(User).where(User.id == assign_data.engineer_id, User.role == "engineer"))
    engineer = engineer_result.scalar_one_or_none()
    if not engineer:
        raise HTTPException(status_code=404, detail="Engineer not found")

    order.engineer_id = engineer.id
    await db.commit()
    await db.refresh(order, attribute_names=['services'])
    return order_to_response(order)

@router.delete("/{order_id}", response_model=dict, dependencies=[Depends(get_manager_or_admin)])
async def delete_order(order_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    await db.delete(order)
    await db.commit()
    return {"message": "Order deleted"}