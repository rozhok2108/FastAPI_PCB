from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.models import UserRole, OrderStatus

class Token(BaseModel):
    access_token: str
    token_type: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserBase(BaseModel):
    email: EmailStr
    role: UserRole = UserRole.CLIENT

class UserCreate(UserBase):
    email: EmailStr
    password: str
    role: str
    class Config:
        from_attributes = True

class UserResponse(UserBase):
    id: int
    class Config:
        from_attributes = True

class ServiceBase(BaseModel):
    name: str
    price: int

class ServiceResponse(ServiceBase):
    id: int
    is_active: bool
    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    description: str
    service_ids: List[int]

class OrderCreate(OrderBase):
    client_id: Optional[int] = None

class OrderStatusUpdate(BaseModel):
    status: OrderStatus

class OrderAssign(BaseModel):
    engineer_id: int

class OrderResponse(BaseModel):
    id: int
    client_id: int
    engineer_id: Optional[int]
    description: str
    status: OrderStatus
    created_at: datetime
    service_ids: List[int]
    
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True