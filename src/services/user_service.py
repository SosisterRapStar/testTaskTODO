from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from src.adapters.repository import AbstractUserRepo
from src.domain.schemas import BaseUserModel
from src.domain.entities import User, Note
from asyncpg.exceptions import UniqueViolationError
from fastapi import HTTPException
from typing import List
from src.domain.schemas import UserOnAuth
from sqlalchemy.exc import IntegrityError

@dataclass
class UserService:
    session: AsyncSession
    user_repo: AbstractUserRepo

    async def register_user(self, user: UserOnAuth) -> User:
        user = await self.user_repo.create(name=user.name, password=user.password)
        try:
            await self.session.commit()
            return user
        except (IntegrityError, UniqueViolationError )as e:
            raise HTTPException(
                status_code=400, detail="User with this nickname already exists"
            )
        

    async def delete_user(self, current_user: User, deleting_id: str) -> str:
        if current_user.id != deleting_id:
            raise HTTPException(status_code=403, detail="No such permissions")
        result = await self.user_repo.delete(id=deleting_id)
        await self.session.commit
        return result.scalar_one()

    async def get_users_notes(self, user: User) -> List[Note]:
        await user.awaitable_attrs.notes
        return user.notes

    async def update_user(self, user: BaseUserModel, user_id: str) -> User:
        updates = user.model_dump(exclude_defaults=True)
        result = await self.user_repo.update(user_id=user_id, updates=updates)
        await self.session.commit()
        return result.scalar_one()
