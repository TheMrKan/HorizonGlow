from aiogram import Router, F
from aiogram.filters import CommandStart, BaseFilter
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, ErrorEvent
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import logging
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from config import instance as config
from core import tickets
from core.models import User

logger = logging.getLogger(__name__)

router = Router(name="user_commands")

default_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=config.user_commands.new_ticket_button)]], resize_keyboard=True)
empty_keyboard = ReplyKeyboardMarkup(keyboard=[], resize_keyboard=True)


class ChatTypeFilter(BaseFilter):
    def __init__(self, chat_type: str | list):
        self.chat_type = chat_type

    async def __call__(self, message: Message) -> bool:
        if isinstance(self.chat_type, str):
            return message.chat.type == self.chat_type
        else:
            return message.chat.type in self.chat_type


@router.error()
async def error_handler(event: ErrorEvent):
    logger.exception("An error occured during handling an event", exc_info=event.exception)
    if event.update.message:
        await event.update.message.answer(config.general.error)


@router.message(ChatTypeFilter("private"), CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(config.user_commands.start_message, reply_markup=default_keyboard)
    await cmd_new_ticket(message, state)


class NewTicketForm(StatesGroup):
    support_code = State()

new_ticket_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=config.user_commands.new_ticket_no_code)]],
                                          resize_keyboard=True)


@router.message(ChatTypeFilter("private"),F.text.casefold() == config.user_commands.new_ticket_button.casefold())
async def cmd_new_ticket(message: Message, state: FSMContext):
    await state.set_state(NewTicketForm.support_code)
    await message.answer(config.user_commands.new_ticket_answer,
                         reply_markup=new_ticket_keyboard)


@router.message(ChatTypeFilter("private"), NewTicketForm.support_code)
async def cmd_new_ticket_support_code(message: Message, session: AsyncSession, user: User, state: FSMContext):
    if message.text.casefold() == config.user_commands.new_ticket_no_code.casefold():
        code = None
    else:
        code = message.text.strip("# \n")
        if len(code) != 4:
            await message.answer(config.user_commands.new_ticket_invalid_code, reply_markup=new_ticket_keyboard)
            return

    try:
        await tickets.create_ticket_async(session, user, code)
        await state.clear()
        await message.answer(config.user_commands.new_ticket_success)

    except tickets.InvalidSupportCodeError:
        await message.answer(config.user_commands.new_ticket_invalid_code, reply_markup=new_ticket_keyboard)

    except tickets.SupportPeriodExpiredError:
        await state.clear()
        await message.answer(config.user_commands.new_ticket_preriod_expired, reply_markup=default_keyboard)

    except tickets.AlreadyHaveTicketError:
        await state.clear()
        await message.answer(config.user_commands.new_ticket_already_have, reply_markup=default_keyboard)

