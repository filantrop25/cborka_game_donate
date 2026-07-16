from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import threading
import asyncio
from aiohttp import web

API_TOKEN = '8858968393:AAHJjzfd-wcKtZllV9w-m9e7VayMTXcnwQ8'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

class DonationStates(StatesGroup):
    waiting_for_amount = State()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.button(text="Пожертвовать ⭐️")
    await message.answer(
        "Приветствуем! Наш проект помогает нуждающимся. "
        "Вы можете сделать любое пожертвование в Telegram Stars.",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )

@dp.message(F.text == "Пожертвовать ⭐️")
async def start_donation(message: types.Message, state: FSMContext):
    await state.set_state(DonationStates.waiting_for_amount)
    await message.answer("Пожалуйста, введите желаемую сумму пожертвования (целое число от 1 до 250 000):")

@dp.message(DonationStates.waiting_for_amount)
async def process_amount(message: types.Message, state: FSMContext):
    user_input = message.text.strip()
    if not user_input.isdigit():
        await message.answer("Ошибка! Пожалуйста, введите корректное число цифрами.")
        return
    amount = int(user_input)
    if amount < 1 or amount > 250000:
        await message.answer("Сумма пожертвования должна быть в диапазоне от 1 до 250 000 ⭐️.")
        return
    await state.clear()
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Благотворительный донат",
        description=f"Добровольное пожертвование в размере {amount} ⭐️",
        payload=f"donation_{message.from_user.id}_{amount}",
        provider_token="",
        currency="XTR",
        prices=[types.LabeledPrice(label="Благотворительность", amount=amount)]
    )

@dp.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.successful_payment)
async def success_payment_handler(message: types.Message):
    stars_received = message.successful_payment.total_amount
    await message.answer(f"Спасибо! Мы успешно получили ваш донат в {stars_received} ⭐️. Проект продолжает жить благодаря вам!")

if __name__ == '__main__':
    dp.run_polling(bot)
