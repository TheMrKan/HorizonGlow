import logging
from aiogram import Router
from aiogram.types import ErrorEvent, Message
from aiogram.filters import BaseFilter
from sqlalchemy.ext.asyncio import AsyncSession

from config import instance as config
from core import tickets

logger = logging.getLogger(__name__)

router = Router(name="support_commands")


@router.error()
async def error_handler(event: ErrorEvent):
    logger.exception("An error occured during handling an event", exc_info=event.exception)
    if event.update.message:
        await event.update.message.answer(config.general.error)


class SupportChatFilter(BaseFilter):

    async def __call__(self, message: Message) -> bool:
        return message.chat.id == config.SUPPORT_GROUP_ID


@router.message(SupportChatFilter())
async def on_message(message: Message, session: AsyncSession):
    if not message.from_user or message.from_user.is_bot:
        return

    try:
        await tickets.send_message_from_support_async(session, message)
    except tickets.NoTicketError:
        await message.answer(config.support_commands.ticket_is_closed)