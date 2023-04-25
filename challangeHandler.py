from loader import dp, bot
from aiogram import types
import requests
from loader import HOST
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
import json


@dp.message_handler(commands="challenge")
async def toChallenge(message: types.Message):
    req = requests.get(HOST + '/api/occupations/states')

    if req.status_code == 200:
        data = req.json()
        if data['data'] is True:
            await message.answer('Стол занят, повторите попытку позже')
            return
    else:
        await message.answer('Сервер не отвечает')
        return

    # Проверка существующего пользователя
    req = requests.get(HOST + '/api/users/find', params={'chat_id': message.chat.id},
                       headers={'Accept': 'application/json'})

    if req.status_code == 404:
        await message.answer('Пользователь не найден')
        return
    elif req.status_code != 200:
        await message.answer('Сервер не отвечает')
        return

    user_data = req.json()['data']

    req = requests.get(HOST + '/api/users/' + str(user_data['id']) + '/settings')

    if req.status_code == 200:
        data = req.json()
        if len(data['data']) == 0:
            inline_kb = InlineKeyboardMarkup(row_width=2)
            json_data = {'cmd': 'side', 'm': 'pvp'}
            json_btn = json.dumps(json_data)
            inline_kb.add(InlineKeyboardButton('PvP', callback_data=json_btn))
            await message.answer('Выбери режим игры', reply_markup=inline_kb)
        else:
            inline_kb = keyboardBuilder(data['data'])
            await message.answer('Выбери шаблон игры', reply_markup=inline_kb)
    else:
        await message.answer('Сервер не отвечает')
        return


async def sideCallback(callback_query: types.CallbackQuery, json_data):
    await bot.answer_callback_query(callback_query.id)

    json_btn = {'cmd': 'color', 'm': json_data['m'], 'side': 'y'}

    inline_kb = InlineKeyboardMarkup(row_width=2)

    btn_data = json.dumps(json_btn)

    accept_btn = InlineKeyboardButton('Да', callback_data=btn_data)

    json_btn['side'] = 'n'

    btn_data = json.dumps(json_btn)

    decline_btn = InlineKeyboardButton('Нет', callback_data=btn_data)

    inline_kb.add(accept_btn, decline_btn)

    await bot.edit_message_text('Учитывать смену сторон?',
                                callback_query.message.chat.id,
                                callback_query.message.message_id,
                                reply_markup=inline_kb)


async def colorCallback(callback_query: types.CallbackQuery, json_data):
    await bot.answer_callback_query(callback_query.id)
    json_data = {'cmd': 'enemy', 'm': json_data['m'], 'side': json_data['side'], 'color': 'r'}
    inline_kb = InlineKeyboardMarkup(row_width=2)
    json_btn = json.dumps(json_data)
    red_side_btn = InlineKeyboardButton('Красная', callback_data=json_btn)
    json_data['color'] = 'b'
    json_btn = json.dumps(json_data)
    blue_btn = InlineKeyboardButton('Синяя', callback_data=json_btn)
    inline_kb.add(red_side_btn, blue_btn)
    await bot.edit_message_text('Выберите сторону',
                                callback_query.message.chat.id,
                                callback_query.message.message_id,
                                reply_markup=inline_kb)


async def saveSettingsToRequest(callback_query: types.CallbackQuery, json_data):
    await bot.answer_callback_query(callback_query.id)

    template_id = saveGameSettingTemplate(callback_query, json_data)

    data = {'id': template_id}

    if template_id:
        await chooseGamerCallback(callback_query, data)


def saveGameSettingTemplate(callback_query: types.CallbackQuery, json_data):

    url = HOST + '/api/settings/store'

    request_data = {
        'chat_id': callback_query.message.chat.id,
        'mode': json_data['m'],
        'side': json_data['color'],
        'change': json_data['side'],
    }

    req = requests.post(url, request_data)

    if req.status_code == 200:
        json_data = req.json()
        if json_data['data'] is True:
            return json_data['id']
        return False


async def chooseGamer(message, state=None, message_edited=False):

    req = requests.get(HOST + '/api/users', params={'chat_id': message.chat.id})

    if req.status_code == 200:
        data = req.json()
        if len(data['data']) == 0:
            if state:
                await state.finish()
            if message_edited:
                await bot.edit_message_text('Сервер не отвечает',
                                            message.chat.id,
                                            message.message_id)
            else:
                await bot.send_message(message.chat.id, 'Сервер не отвечает')

        inline_kb = InlineKeyboardMarkup(row_width=1)

        for item in data:
            login = item.get('login', '')
            chat_id = item.get('telegram_chat_id', '')
            if len(login) == 0 or len(chat_id) == 0:
                continue
            btn = InlineKeyboardButton(login, callback_data=chat_id)
            inline_kb.add(btn)
        # await GameSettings.next()
        if message_edited:
            await bot.edit_message_text('Выбери соперника',
                                        message.chat.id,
                                        message.message_id,
                                        reply_markup=inline_kb)
        else:
            await bot.send_message(message.chat.id,
                                   'Выбери соперника',
                                   reply_markup=inline_kb)
    else:
        if state:
            await state.finish()
        if message_edited:
            await bot.edit_message_text('Сервер не отвечает',
                                        message.chat.id,
                                        message.message_id)
        else:
            await bot.send_message(message.chat.id, 'Сервер не отвечает')


async def chooseGamerCallback(callback_query: types.CallbackQuery, json_data):

    req = requests.get(HOST + '/api/users', params={'chat_id': callback_query.message.chat.id})

    if req.status_code == 200:
        data = req.json()
        if len(data['data']) == 0:
            await bot.edit_message_text('Игроков не найдено',
                                        callback_query.message.chat.id,
                                        callback_query.message.message_id)
        inline_kb = InlineKeyboardMarkup(row_width=1)
        for item in data['data']:
            login = item.get('login', '')
            chat_id = item.get('telegram_chat_id', '')
            if len(login) == 0 or len(chat_id) == 0:
                continue
            json_data = {'cmd': 'request', 'id': json_data['id'], 'ch_id': chat_id}
            jsonBtn = json.dumps(json_data)
            btn = InlineKeyboardButton(login, callback_data=jsonBtn)
            inline_kb.add(btn)
        await bot.edit_message_text('Выбери соперника',
                                    callback_query.message.chat.id,
                                    callback_query.message.message_id,
                                    reply_markup=inline_kb)
    else:
        await bot.edit_message_text('Сервер не отвечает',
                                    callback_query.message.chat.id,
                                    callback_query.message.message_id)


async def requestToGamer(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    stateData = await state.get_data()
    await state.finish()
    # await sendToRecipient(callback_query, stateData['t_id'])


async def requestToGamerCallback(callback_query: types.CallbackQuery, json_data):

    req = requests.get(HOST + '/api/settings/' + str(json_data['id']))

    if req.status_code == 200:
        data = req.json()
        settings = data['data']
        if settings['mode'] == 'pvp':
            mode_game = 'Режим: PvP \n'
        else:
            mode_game = 'Режим: TvT \n'
        if settings['side'] == 'red':
            side_game = 'За сторону синих \n'
        else:
            side_game = 'За сторону красных \n'
        if settings['side_change'] == 1:
            side_change = 'Со сменой сторон \n'
        else:
            side_change = 'Без смены сторон \n'

        from_user_name = callback_query.message.chat.first_name
        text = 'Пользователь ' + from_user_name + ' рискнул бросить тебе вызов: \n'

        text += mode_game + side_game + side_change

        send_data = {'cmd': 'accept', 'f': callback_query.message.chat.id, 'id': settings['id'], 'd': True}

        accept_json = json.dumps(send_data)

        send_data['d'] = False

        decline_json = json.dumps(send_data)

        inline_kb = InlineKeyboardMarkup(row_width=2)

        accept_btn = InlineKeyboardButton('Принять', callback_data=accept_json)

        decline_btn = InlineKeyboardButton('Я ссыкло', callback_data=decline_json)

        inline_kb.add(accept_btn, decline_btn)

        await bot.send_message(json_data['ch_id'],
                               text,
                               reply_markup=inline_kb)

        #Ответ бросившему вызов
        await bot.edit_message_text('Ждем ответа от игрока',
                                    callback_query.message.chat.id,
                                    callback_query.message.message_id)
    else:
        await bot.edit_message_text('Сервер не отвечает',
                                    callback_query.message.chat.id,
                                    callback_query.message.message_id)

def keyboardBuilder(settings):
    inline_kb = InlineKeyboardMarkup(row_width=1)
    for item in settings:
        if item['mode'] == 'pvp':
            text_btn = 'PvP.'
        else:
            text_btn = 'TvT.'
        if item['side'] == 'red':
            text_btn += ' За красных.'
        else:
            text_btn += ' За синих.'
        if item['side_change'] == 1:
            text_btn += ' Со сменой сторон.'
        else:
            text_btn += ' Без смены сторон.'
        json_data = {'cmd': 'template', 'id': item['id']}
        json_btn = json.dumps(json_data)
        inline_btn = InlineKeyboardButton(text_btn, callback_data=json_btn)
        inline_kb.add(inline_btn)
    return inline_kb
