from loader import dp, bot
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loader import WS_HOST
from websockets import connect
import json


async def acceptChallengeHandler(callback_query: types.CallbackQuery, json_data):
    # inline_kb = None
    if json_data['d'] is True:

        text = 'Вызов принят'

        text_to_sender = 'Наконец-то достойный противник'

        # inline_kb = InlineKeyboardMarkup(row_width=1)
        # callback_data = {'cmd': 'start'}

        # json_btn = json.dumps(callback_data)
        #
        # inline_btn = InlineKeyboardButton('Старт', callback_data=json_btn)
        #
        # inline_kb.add(inline_btn)

        json_data['r'] = callback_query.message.chat.id

        json_data['cmd'] = 'prepare'

        json_data['t_id'] = json_data['id']

        await socketSend(json_data)

    else:
        text = 'Он признал себя ссыклом'

        text_to_sender = 'Достаточно крысиный поступок'

    await bot.send_message(json_data['f'], text)

    await bot.edit_message_text(text_to_sender,
                                callback_query.message.chat.id,
                                callback_query.message.message_id)


async def startGame(callback_query: types.CallbackQuery, json_data):
    socket_data = {'cmd': 'start'}

    await socketSend(socket_data)

    await bot.edit_message_text('Игра началась',
                                callback_query.message.chat.id,
                                callback_query.message.message_id)


async def socketSend(data):
    async with connect(WS_HOST) as socket:
        await socket.send(json.dumps(data))
