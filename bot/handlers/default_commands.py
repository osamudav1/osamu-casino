from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from fluent.runtime import FluentLocalization

from bot.config_reader import GameConfig
from bot.keyboards import get_spin_keyboard
from bot.db import get_user_balance

flags = {"throttling_key": "default"}
router = Router()


@router.message(Command("start"), flags=flags)
async def cmd_start(
        message: Message,
        state: FSMContext,
        l10n: FluentLocalization,
        game_config: GameConfig,
):
    user_id = message.from_user.id
    current_balance = await get_user_balance(user_id, game_config.starting_points)
    
    start_text = l10n.format_value("start-text", {"points": current_balance})

    await state.update_data(score=current_balance)
    await message.answer(start_text, reply_markup=get_spin_keyboard(l10n))


@router.message(Command("stop"), flags=flags)
async def cmd_stop(message: Message, l10n: FluentLocalization):
    await message.answer(
        l10n.format_value("stop-text"),
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(Command("help"), flags=flags)
async def cmd_help(message: Message, l10n: FluentLocalization):
    await message.answer(
        l10n.format_value("help-text"),
        disable_web_page_preview=True
    )
