from loader import dp, bot
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loader import WS_HOST
from websockets import connect
import json


async def acceptChallengeHandler(callback_query: types.CallbackQuery, jsonData):
    inlineKb = None
    if jsonData['d'] is True:
        text = 'Вызов принят'
        textToSender = 'Наконец-то достойный противник'
        inlineKb = InlineKeyboardMarkup(row_width=1)
        callbackData = {'cmd': 'start'}
        jsonBtn = json.dumps(callbackData)
        inlineBtn = InlineKeyboardButton('Старт', callback_data=jsonBtn)
        inlineKb.add(inlineBtn)
        jsonData['r'] = callback_query.message.chat.id
        jsonData['cmd'] = 'prepare'
        jsonData['t_id'] = jsonData['id']
        await socketSend(jsonData)

    else:
        text = 'Он признал себя ссыклом'
        textToSender = 'Достаточно крысиный поступок'
    await bot.send_message(jsonData['f'], text)

    await bot.edit_message_text(textToSender,
                                callback_query.message.chat.id,
                                callback_query.message.message_id,
                                reply_markup=inlineKb)


async def startGame(callback_query: types.CallbackQuery, jsonData):
    socketData = {'cmd': 'start'}
    await socketSend(socketData)
    await bot.edit_message_text('Игра началась',
                                callback_query.message.chat.id,
                                callback_query.message.message_id)


async def socketSend(data):
    async with connect(WS_HOST) as socket:
        await socket.send(json.dumps(data))
