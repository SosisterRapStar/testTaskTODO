from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSessions
from src.adapters.repository import AbstractUserRepo
from src.domain.schemas import BaseUserModel
from src.domain.entities import User, Note
from asyncpg.exceptions import UniqueViolationError
from fastapi import HTTPException
from typing import List

@dataclass
class UserService:
    session: AsyncSessions
    user_repo: AbstractUserRepo

    async def create_user(self, user: BaseUserModel) -> User:
        try:
            user = await self.user_repo.create(user.name, user.password)
            await self.session.commit()
        except UniqueViolationError as e:
            raise HTTPException(status_code=400, detail="User with this nickname already exists")
        
    async def delete_user(self, current_user: User, deleting_id: str) -> str:
        if current_user.id != deleting_id:
            raise HTTPException(status_code=403, detail="No such permissions")
        result = await self.user_repo.delete(id=deleting_id)
        await self.session.commit
        return result.scalar_one()
    
    async def get_users_notes(self, current_user: User) -> List[Note]:
        return User.notes
    
    async def update_user(self, user: BaseUserModel, user_id: str) -> User:
        updates = user.model_dump(exclude_defaults=True)
        result = await self.user_repo.update(user_id = user_id, updates=updates)
        await self.session.commit()
        return result.scalar_one()
