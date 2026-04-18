import enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Table,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class UserRole(str, enum.Enum):
    GUEST = "guest"
    CLIENT = "client"
    ENGINEER = "engineer"
    MANAGER = "manager"
    ADMIN = "admin"


class OrderStatus(str, enum.Enum):
    NEW = "new"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    READY = "ready"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


order_services = Table(
    "order_services",
    Base.metadata,
    Column("order_id", Integer, ForeignKey("orders.id"), primary_key=True),
    Column("service_id", Integer, ForeignKey("services.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.CLIENT)
    orders_created = relationship(
        "Order", back_populates="client", foreign_keys="Order.client_id"
    )
    orders_assigned = relationship(
        "Order", back_populates="engineer", foreign_keys="Order.engineer_id"
    )


class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    price = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    orders = relationship("Order", secondary=order_services, back_populates="services")


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    engineer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    description = Column(String)
    status = Column(
        Enum(
            OrderStatus,
            name="orderstatus",
            values_callable=lambda x: [e.value for e in x],
        ),
        default=OrderStatus.NEW,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    client = relationship(
        "User", foreign_keys=[client_id], back_populates="orders_created"
    )
    engineer = relationship(
        "User", foreign_keys=[engineer_id], back_populates="orders_assigned"
    )
    services = relationship(
        "Service", secondary=order_services, back_populates="orders"
    )
