import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_password_hash
from app.models import User, UserRole

logger = logging.getLogger(__name__)


async def create_default_admin(db: AsyncSession, email: str, password: str) -> bool:
    """
    Создает пользователя с ролью admin, если он ещё не существует.
    Возвращает True, если админ был создан, False если уже существовал.
    """
    # Проверяем, есть ли уже админ с таким email
    result = await db.execute(select(User).where(User.email == email))
    existing_admin = result.scalar_one_or_none()

    if existing_admin:
        logger.info(f"✅ Admin user '{email}' already exists, skipping creation")
        return False

    # Создаем нового админа
    admin = User(
        email=email, hashed_password=get_password_hash(password), role=UserRole.ADMIN
    )

    db.add(admin)
    await db.commit()
    await db.refresh(admin)

    logger.info(f"🎉 Default admin created: {email}")
    logger.info(f"   🔐 Password: {password}  ← ИЗМЕНИТЕ ПОСЛЕ ПЕРВОГО ВХОДА!")

    return True
