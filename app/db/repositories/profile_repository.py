from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm.users import UserProfile

class ProfileRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_id(self, user_id: UUID) -> Optional[UserProfile]:
        result = await self.session.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )

        return result.scalars().first()
    
    async def create_or_update(self, user_id: UUID, profile_data: dict) -> Optional[UserProfile]:
        profile = await self.get_by_user_id(user_id=user_id)
        if profile:
            for key, value in profile_data.items():
                setattr(profile, key, value)

        else:
            profile = UserProfile(user_id=user_id, **profile_data)
            self.session.add(profile)

        await self.session.commit()
        return profile