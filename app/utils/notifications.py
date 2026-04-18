import logging
logger = logging.getLogger("notifications")

async def send_order_status_notification(email: str, status: str):
    # Здесь была бы отправка Email или Telegram
    logger.info(f"NOTIFICATION SENT to {email}: Order status is now {status}")
    return True