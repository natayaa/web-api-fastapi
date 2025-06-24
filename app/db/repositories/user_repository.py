from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm.users import User
from app.models.schemas.user import UserCreate, UserUpdate

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.user_id == user_id)
        )

        return result.scalars().first()
    
    async def get_by_mail(self, email: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )

        return result.scalars().first()
    
    async def create(self, user_data: UserCreate, hashed_password: str) -> User:
        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            profile=None
        )

        self.session.add(user)
        await self.session.commit()
        return user
    
    async def update(self, user_id: UUID, update_data = UserUpdate) -> Optional[User]:
        await self.session.execute(
            update(User)
            .where(User.user_id == user_id)
            .values(**update_data.model_dump(exclude_unset=True))
        )

        await self.session.commit()
        return await self.get_by_id(user_id)