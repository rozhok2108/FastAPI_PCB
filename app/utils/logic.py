from app.models import OrderStatus

ALLOWED_TRANSITIONS = {
    OrderStatus.NEW: [
        OrderStatus.ACCEPTED,
        OrderStatus.IN_PROGRESS,
        OrderStatus.CANCELLED,
    ],
    OrderStatus.ACCEPTED: [OrderStatus.IN_PROGRESS, OrderStatus.CANCELLED],
    OrderStatus.IN_PROGRESS: [OrderStatus.READY, OrderStatus.CANCELLED],
    OrderStatus.READY: [OrderStatus.SHIPPED, OrderStatus.DELIVERED],
    OrderStatus.SHIPPED: [OrderStatus.DELIVERED],
    OrderStatus.DELIVERED: [],
    OrderStatus.CANCELLED: [],
}


def validate_status_transition(current: OrderStatus, new: OrderStatus) -> bool:
    return new in ALLOWED_TRANSITIONS.get(current, [])
