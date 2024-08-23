import asyncio
import logging
import os
import sys
from gc import callbacks
from http.client import responses

from aiogram import Bot, Dispatcher, F, html
from aiogram import types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ContentType
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv
from api_cuntions import get_all_tests, user_solved, check_test, get_test_by_id, add_file

load_dotenv()

TOKEN = os.getenv("TOKEN")
dp = Dispatcher(storage=MemoryStorage())


class TestState(StatesGroup):
    test = State()
    solution = State()


@dp.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    await message.answer("Assalomu Aleykum test yechish uchun shu buyriqni yuboring\n/testlar")


@dp.message(Command('testlar'))
async def command_testlar_handler(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    if not data.get('test'):
        tests = await get_all_tests()
        builder = InlineKeyboardBuilder()
        if tests:
            for test in tests:
                builder.button(text=test['test_name'],
                               callback_data=f"testlar_{test["id"]}_{message.from_user.id}_{test['test_name']}")
            builder.adjust(2)
            await message.answer("Testlardan birini tanlang!", reply_markup=builder.as_markup())
            await state.set_state(TestState.test)
        else:
            await message.answer("Hali testlar kiritilmagan")
            await state.clear()
    else:
        await message.reply(
            f"Siz testni boshlab qo'ygansiz u testni yakunlang!\nKalitlarini Ko'rsatilgan tartibda yozib yuboring!\nAgar testni yechishni istamasangiz {html.bold("yakunlash")} so'zini yozib yuboring!")
        await state.clear()


@dp.callback_query(lambda callback: callback.data.startswith('testlar'), TestState.test)
async def options_test_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    data_call = callback.data.split('_')
    test_name = data_call[3]
    test_id = data_call[1]
    telegram_id = data_call[2]
    await state.update_data(test=test_id)
    await callback.message.edit_text(f"{test_name.capitalize()} tanlandi")

    response = await user_solved(pk=test_id, telegram_id=telegram_id)
    if response['solved']:
        await callback.message.reply(
            f"Siz oldin bu testni yechgansiz\nNatija: {response['question_quantity']}/{response['result']}")
        await state.clear()
    else:
        caption = f'''Test boshlandi kalitlarini namunada ko'rsatilgandek yuboring
        
{html.bold("abcdaabb...")}
Agar testni yechishni istamasangiz {html.bold("yakunlash")} so'zini yozib yuboring
        '''
        response_file_id = await get_test_by_id(test_id)
        file_id = response_file_id['test_files']
        if file_id:
            file_id = file_id[0]['file_id']
            await callback.message.answer_document(document=file_id)
        await callback.message.reply(caption)
        await state.set_state(TestState.solution)


@dp.message(F.content_type == ContentType.TEXT, TestState.solution)
async def solution_test_handler(message: types.Message, state: FSMContext) -> None:
    solution = message.text
    await state.update_data(solution=solution)
    if not solution.isalpha() or solution.lower() == "yakunlash":
        solution = "∅"
    name = message.from_user.full_name
    telegram_id = message.from_user.id

    data = await state.get_data()
    test_id = data.get('test')

    response = await check_test(solution=solution, telegram_id=telegram_id, name=name, pk=test_id)
    if response.get('result') or response.get('result') >= 0:
        await message.reply(f"Natija: {response['question_quantity']}/{response['result']}")
    elif response.get('error'):
        await message.reply(f"{response['error']}")
    else:
        await message.reply("Serverda xatolik. Dasturchiga aloqa chiqing @IbraigmovQuovnchbek")

    await state.clear()


@dp.message(F.content_type == ContentType.DOCUMENT)
async def document_message_handler(message: types.Message) -> None:
    if message.from_user.id == 5091336899:
        try:
            file_id = message.document.file_id
            file_caption = int(message.caption)
            response = await add_file(file_caption, file_id)
            if response.get('status'):
                await message.reply("Bazaga qo'shildi")
            else:
                await message.reply("Serverda Xatolik. Dasturchiga aloqa chiqing @IbraigmovQuovnchbek")
        except Exception as e:
            await message.reply("Serverda Xatolik. Dasturchiga aloqa chiqing @IbraigmovQuovnchbek")


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
