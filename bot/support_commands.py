import logging
from aiogram import Router, html, F
from aiogram.types import ErrorEvent, Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, \
    InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ForumTopicClosed
from aiogram.filters import BaseFilter
from sqlalchemy.ext.asyncio import AsyncSession
import datetime

from config import instance as config
from core import tickets
from core.models import Ticket
from core.api import ProductInfo
import globals

logger = logging.getLogger(__name__)

router = Router(name="support_commands")


def format_dt(dt: datetime.datetime) -> str:
    return datetime.datetime.strftime(dt, '%m/%d/%Y %H:%M UTC')


ticket_start_message_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=config.support_commands.close_ticket_button, callback_data="close_ticket")]])


async def on_ticket_created_async(ticket: Ticket, product: ProductInfo | None, **kwargs):
    message = f"[{ticket.id}] Ticket created"

    if product:
        message += (f"\n\n{html.bold("Product info:")}\n"
                    f"{html.bold("File:")} {html.code(product.file_name)}\n"
                    f"{html.bold("Description:")} {product.description}\n"
                    f"{html.bold("Support code:")} {product.support_code}\n"
                    f"{html.bold("State:")} {product.score}\n"
                    f"{html.bold("Balance:")} {product.number}\n"
                    f"{html.bold("Price:")} {product.price}$\n"
                    f"{html.bold("Produced at:")} {format_dt(product.produced_at)}\n"
                    f"{html.bold("Purchased at:")} {format_dt(product.purchased_at)}")
    else:
        message += f"\n\n{html.bold("Product is not provided")}"

    message += "\n\nAll messages in this chat will be sent to the ticket creator"

    await globals.bot.send_message(config.SUPPORT_GROUP_ID, message, message_thread_id=ticket.topic_id, reply_markup=ticket_start_message_keyboard)


tickets.emitter.on("created", on_ticket_created_async)


class SupportChatFilter(BaseFilter):

    async def __call__(self, obj: Message | CallbackQuery) -> bool:
        if isinstance(obj, CallbackQuery):
            obj = obj.message

        return obj.chat.id == config.SUPPORT_GROUP_ID


@router.callback_query(SupportChatFilter(),  F.data == "close_ticket")
async def close_ticket_callback(callback_query: CallbackQuery, session: AsyncSession):
    await tickets.close_topic_ticket_async(session, callback_query.message.message_thread_id)
    await callback_query.answer()


@router.error()
async def error_handler(event: ErrorEvent):
    logger.exception("An error occured during handling an event", exc_info=event.exception)
    if event.update.message:
        await event.update.message.answer(config.general.error)


@router.message(SupportChatFilter(), F.text.casefold() == config.support_commands.close_ticket_button.casefold())
async def close_ticket(message: Message, session: AsyncSession):
    await tickets.close_topic_ticket_async(session, message.message_thread_id)


@router.message(SupportChatFilter())
async def on_message(message: Message, session: AsyncSession):
    if message.forum_topic_closed and message.from_user and not message.from_user.is_bot:
        try:
            await tickets.close_topic_ticket_async(session, message.message_thread_id)
        except tickets.NoTicketError:
            pass
        return

    if any((message.forum_topic_created, message.forum_topic_edited, message.forum_topic_reopened)):
        return

    if not message.from_user or message.from_user.is_bot:
        return

    try:
        await tickets.send_message_from_support_async(session, message)
    except tickets.NoTicketError:
        await message.answer(config.support_commands.ticket_is_closed)


async def on_message_from_user(user: User, message: Message, ticket: Ticket):
    await globals.bot.forward_message(config.SUPPORT_GROUP_ID, user.id, message.message_id,
                                      message_thread_id=ticket.topic_id)


tickets.emitter.on("message_from_user", on_message_from_user)


