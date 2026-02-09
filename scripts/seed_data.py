"""
Seed script - creates admin user and initial data in PostgreSQL.

IMPORTANT: Run inside the backend container to ensure bcrypt compatibility.

    docker compose exec backend python -c "
    import asyncio
    from app.core.database import async_session, engine
    from app.models.sql.user import User
    from sqlalchemy import select
    from passlib.context import CryptContext
    import uuid

    pwd = CryptContext(schemes=['bcrypt'], deprecated='auto')

    async def seed():
        async with async_session() as s:
            r = await s.execute(select(User).where(User.username == '29449799814'))
            if r.scalar_one_or_none():
                print('Admin already exists')
            else:
                s.add(User(id=uuid.uuid4(), email='admin@tennistrack.app', username='29449799814',
                    full_name='Administrador', password=pwd.hash('Theo78745382!'), role='admin',
                    is_active=True, language='pt-BR', email_verified=True,
                    subscription={'plan':'grand_slam','status':'active','stripe_customer_id':None,
                    'stripe_subscription_id':None,'current_period_start':None,
                    'current_period_end':None,'cancel_at_period_end':False,'trial_end':None}))
                print('Admin created')
            await s.commit()
        await engine.dispose()

    asyncio.run(seed())
    "
"""
import asyncio
import uuid
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Admin credentials
ADMIN_USERNAME = "29449799814"
ADMIN_EMAIL = "admin@tennistrack.app"
ADMIN_PASSWORD = "Theo78745382!"
ADMIN_FULL_NAME = "Administrador"

SUBSCRIPTION_GRAND_SLAM = {
    "plan": "grand_slam",
    "status": "active",
    "stripe_customer_id": None,
    "stripe_subscription_id": None,
    "current_period_start": None,
    "current_period_end": None,
    "cancel_at_period_end": False,
    "trial_end": None,
}


async def seed():
    """Create admin user in PostgreSQL via SQLAlchemy ORM."""
    from app.core.database import async_session, engine
    from app.models.sql.user import User
    from sqlalchemy import select

    async with async_session() as session:
        result = await session.execute(
            select(User).where(
                (User.username == ADMIN_USERNAME) | (User.email == ADMIN_EMAIL)
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            print(f"Admin already exists (id: {existing.id}), updating role...")
            existing.role = "admin"
            existing.is_active = True
            existing.email_verified = True
            existing.subscription = SUBSCRIPTION_GRAND_SLAM
        else:
            user = User(
                id=uuid.uuid4(),
                email=ADMIN_EMAIL,
                username=ADMIN_USERNAME,
                full_name=ADMIN_FULL_NAME,
                password=pwd_context.hash(ADMIN_PASSWORD),
                role="admin",
                is_active=True,
                language="pt-BR",
                email_verified=True,
                subscription=SUBSCRIPTION_GRAND_SLAM,
            )
            session.add(user)
            print(f"Admin user created: {ADMIN_USERNAME} (id: {user.id})")

        await session.commit()

    await engine.dispose()
    print("Seed complete!")


if __name__ == "__main__":
    asyncio.run(seed())
