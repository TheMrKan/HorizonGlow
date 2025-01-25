from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa
from aiogram import html
from aiogram.types import Message
import datetime

from core.api import APIClient, ProductInfo
from .models import User, Ticket
import globals
from config import instance as config


class InvalidSupportCodeError(Exception):
    pass


class SupportPeriodExpiredError(Exception):
    pass


class AlreadyHaveTicketError(Exception):
    pass


async def create_ticket_async(db: AsyncSession, user: User, support_code: str | None):
    if user.ticket:
        raise AlreadyHaveTicketError

    product = None
    if support_code:
        product = await APIClient.instance.fetch_product_by_support_code_async(support_code)
        if not product or not product.purchased_by:
            raise InvalidSupportCodeError

        if product.is_support_period_expired:
            raise SupportPeriodExpiredError

    ticket_id = await __get_id_async(db)

    topic = await globals.bot.create_forum_topic(config.SUPPORT_GROUP_ID, f"[{ticket_id}] Ticket: {'No Product' if not product else product.description}", icon_color=9367192)

    try:
        ticket = Ticket(id=ticket_id, topic_id=topic.message_thread_id)
        db.add(ticket)
        user.ticket = ticket.id
        await db.commit()
    except:
        await globals.bot.delete_forum_topic(config.SUPPORT_GROUP_ID, topic.message_thread_id)
        raise

    await __send_ticket_info_async(ticket, product)
    return ticket, product


async def __get_id_async(db: AsyncSession):
    query = sa.select(sa.func.max(Ticket.__table__.c.id))
    return ((await db.execute(query)).scalar_one_or_none() or 0) + 1


def format_dt(dt: datetime.datetime) -> str:
    return datetime.datetime.strftime(dt, '%m/%d/%Y %H:%M UTC')


async def __send_ticket_info_async(ticket: Ticket, product: ProductInfo | None):
    message = f"[{ticket.id}] Ticket created"

    if product:
        message += (f"\n\n{html.bold("Product info:")}\n"
                    f"{html.bold("Description:")} {product.description}\n"
                    f"{html.bold("Support code:")} {product.support_code}\n"
                    f"{html.bold("Score:")} {product.score}\n"
                    f"{html.bold("Number:")} {product.number}\n"
                    f"{html.bold("Price:")} {product.price}$\n"
                    f"{html.bold("Produced at:")} {format_dt(product.produced_at)}\n"
                    f"{html.bold("Purchased at:")} {format_dt(product.purchased_at)}")
    else:
        message += f"\n\n{html.bold("Product is not provided")}"

    message += "\n\nAll messages in this chat will be sent to the ticket creator"

    await globals.bot.send_message(config.SUPPORT_GROUP_ID, message, message_thread_id=ticket.topic_id)


async def get_ticket_async(db: AsyncSession, ticket_id: int) -> Ticket | None:
    ticket_query = sa.select(Ticket).where(Ticket.id == ticket_id).limit(1)
    return (await db.execute(ticket_query)).scalar_one_or_none()


class NoTicketError(Exception):
    pass


async def __get_active_ticket_user_async(db: AsyncSession, user: User) -> Ticket:
    if not user.ticket:
        raise NoTicketError

    ticket = await get_ticket_async(db, user.ticket)
    if not ticket:
        user.ticket = None
        await db.commit()

        raise NoTicketError

    if ticket.status != ticket.OPENED:
        user.ticket = None
        await db.commit()

        raise NoTicketError

    return ticket


async def close_ticket_async(db: AsyncSession, user: User):
    ticket = await __get_active_ticket_user_async(db, user)

    ticket.status = ticket.CLOSED
    user.ticket = None

    await globals.bot.close_forum_topic(config.SUPPORT_GROUP_ID, ticket.topic_id)
    await globals.bot.edit_forum_topic(config.SUPPORT_GROUP_ID, ticket.topic_id, name=f"[CLOSED] [{ticket.id}]", icon_custom_emoji_id='5420216386448270341')


async def send_message_from_user_async(db: AsyncSession, user: User, message: Message):
    ticket = await __get_active_ticket_user_async(db, user)

    await globals.bot.copy_message(config.SUPPORT_GROUP_ID, user.id, message.message_id, message_thread_id=ticket.topic_id)


async def __get_active_ticket_topic_async(db: AsyncSession, topic_id: int) -> Ticket:
    ticket_query = sa.select(Ticket).where(Ticket.topic_id == topic_id).limit(1)
    ticket = (await db.execute(ticket_query)).scalar_one_or_none()

    if ticket is None or ticket.status != ticket.OPENED:
        raise NoTicketError

    return ticket


async def __get_ticket_user_async(db: AsyncSession, ticket_id: int) -> User | None:
    user_query = sa.select(User).where(User.ticket == ticket_id).limit(1)
    return (await db.execute(user_query)).scalar_one_or_none()


async def send_message_from_support_async(db: AsyncSession, message: Message):
    ticket = await __get_active_ticket_topic_async(db, message.message_thread_id)
    user = await __get_ticket_user_async(db, ticket.id)

    if not user:
        ticket.status = ticket.CLOSED
        await db.commit()
        raise NoTicketError

    await globals.bot.copy_message(user.id, config.SUPPORT_GROUP_ID, message.message_id)
