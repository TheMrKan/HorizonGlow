from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from core.api import APIClient
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
        user.ticket = ticket.id
        await db.commit()
    except:
        await globals.bot.delete_forum_topic(config.SUPPORT_GROUP_ID, topic.message_thread_id)
        raise


async def __get_id_async(db: AsyncSession):
    query = sa.select(sa.func.max(Ticket.__table__.c.id))
    return ((await db.execute(query)).scalar_one_or_none() or 0) + 1

