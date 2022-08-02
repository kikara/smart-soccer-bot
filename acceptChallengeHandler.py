from loader import dp, bot
from aiogram import types
import requests
from loader import HOST
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
import json
from loader import WS_HOST
import asyncio
from websockets import connect


class AcceptChallenge(StatesGroup):
    start = State()


async def acceptChallengeHandler(callback_query: types.CallbackQuery, jsonData):
    await bot.answer_callback_query(callback_query.id)
    inlineKb = None
    if jsonData['d'] is True:
        text = 'Вызов принят'
        textToSender = 'Наконец-то достойный противник'
        inlineKb = InlineKeyboardMarkup(row_width=1)
        inlineBtn = InlineKeyboardButton('Старт', callback_data='start')
        inlineKb.add(inlineBtn)
        await AcceptChallenge.start.set()
        jsonData['r'] = callback_query.message.chat.id
        await sendPrepareGame(jsonData)

    else:
        text = 'Он признал себя ссыклом'
        textToSender = 'Достаточно крысиный поступок'
    await bot.send_message(jsonData['f'], text)

    await bot.edit_message_text(textToSender,
                                callback_query.message.chat.id,
                                callback_query.message.message_id,
                                reply_markup=inlineKb)


@dp.callback_query_handler(lambda callback_query: True, state=AcceptChallenge.start)
async def startGame(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()

    jsonData = {'cmd': 'start'}
    async with connect(WS_HOST) as socket:
        await socket.send(json.dumps(jsonData))
    await bot.edit_message_text('Игра началась',
                                callback_query.message.chat.id,
                                callback_query.message.message_id)


async def sendPrepareGame(jsonData):
    jsonData['cmd'] = 'prepare'
    async with connect(WS_HOST) as socket:
        await socket.send(json.dumps(jsonData))
