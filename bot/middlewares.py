from typing import Callable, Awaitable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
import sqlalchemy as sa

from core.models import User


class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        super().__init__()
        self.session_pool = session_pool

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        async with self.session_pool() as session:
            data["session"] = session
            try:
                result = await handler(event, data)
                await session.commit()
                return result
            except:
                await session.rollback()
                raise


class UsersMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:
        if event.chat.type == "private":
            session: AsyncSession = data["session"]

            new_user = False
            user_query = sa.select(User).where(User.id == event.from_user.id).limit(1)
            user = (await session.execute(user_query)).scalar_one_or_none()

            if not user:
                user = User(id=event.from_user.id)
                session.add(user)

            data["user"] = user
            data["new_user"] = new_user

        return await handler(event, data)