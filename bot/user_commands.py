from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, ErrorEvent
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import logging
from config import instance as config

logger = logging.getLogger(__name__)

router = Router(name="user_commands")

empty_keyboard = ReplyKeyboardMarkup(keyboard=[], resize_keyboard=True)


@router.error()
async def error_handler(event: ErrorEvent):
    logger.exception("An error occured during handling an event", exc_info=event.exception)
    if event.update.message:
        await event.update.message.answer(config.general.error, reply_markup=ReplyKeyboardRemove())


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(config.user_commands.start_message, reply_markup=ReplyKeyboardRemove())
    await cmd_new_ticket(message, state)


class NewTicketForm(StatesGroup):
    support_code: str


@router.message(F.text.casefold() == config.user_commands.new_ticket_button.casefold())
async def cmd_new_ticket(message: Message, state: FSMContext):
    await state.set_state(NewTicketForm.support_code)
    await message.answer(config.user_commands.new_ticket_answer, reply_markup=ReplyKeyboardRemove())


@router.message(NewTicketForm.support_code)
async def cmd_new_ticket_support_code(message: Message, state: FSMContext):
    code = message.text.strip()