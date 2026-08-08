from asyncio import sleep
from contextlib import suppress

from aiogram import Router
from aiogram.enums.dice_emoji import DiceEmoji
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from fluent.runtime import FluentLocalization

from bot.config_reader import GameConfig
from bot.dice_check import get_combo_text, get_score_change
from bot.filters import SpinTextFilter
from bot.keyboards import get_spin_keyboard
from bot.db import get_user_balance, update_user_balance

flags = {"throttling_key": "spin"}
router = Router()


@router.message(Command("spin"), flags=flags)
@router.message(SpinTextFilter(), flags=flags)
async def cmd_spin(
        message: Message,
        state: FSMContext,
        l10n: FluentLocalization,
        game_config: GameConfig,
):
    user_id = message.from_user.id
    # Get current score from MongoDB
    user_score = await get_user_balance(user_id, game_config.starting_points)

    if user_score <= 0:
        if game_config.send_gameover_sticker:
            with suppress(TelegramBadRequest):
                await message.answer_sticker(l10n.format_value("zero-balance-sticker"))
        await message.answer(l10n.format_value("zero-balance"))
        return

    # Send dice to user
    msg = await message.answer_dice(emoji=DiceEmoji.SLOT_MACHINE, reply_markup=get_spin_keyboard(l10n))

    # Check whether user won or not
    score_change = get_score_change(msg.dice.value)

    if score_change < 0:
        win_or_lose_text = l10n.format_value("spin-fail")
    else:
        win_or_lose_text = l10n.format_value("spin-success", {"score-value": score_change})

    # Updating score in MongoDB and FSM data
    new_score = user_score + score_change
    if new_score < 0:
        new_score = 0

    await update_user_balance(user_id, new_score)
    await state.update_data(score=new_score)

    # This delay is roughly equivalent of animation duration
    await sleep(2.0)
    await msg.reply(
        l10n.format_value(
            "after-spin",
            {
                "combo_text": get_combo_text(msg.dice.value, l10n),
                "dice_value": msg.dice.value,
                "result_text": win_or_lose_text,
                "score-value": new_score
            }
        )
    )
