from loader import dp, bot
from aiogram import types
import requests
from loader import HOST
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
import json


@dp.message_handler(commands="challenge")
async def toChallenge(message: types.Message):
    # Проверка существующего пользователя
    req = requests.post(HOST + '/api/bot/checkUser', {'chat_id': message.chat.id})
    if req.status_code == 200:
        data = req.json()
        if data['data'] is False:
            await message.answer('Пожалуйста сначала зарегистрируйтесь')
            return
    else:
        await message.answer('Сервер не отвечает')
        return

    req = requests.post(HOST + '/api/bot/isTableOccupied')
    if req.status_code == 200:
        data = req.json()
        if data['data'] is False:
            await message.answer('Стол занят, повторите попытку позже')
            return
    else:
        await message.answer('Сервер не отвечает')
        return

    req = requests.post(HOST + '/api/bot/getGameSettings', {'chat_id': message.chat.id})
    if req.status_code == 200:
        data = req.json()
        if data['data'] is False:
            inlineKb = InlineKeyboardMarkup(row_width=2)
            jsonData = {'cmd': 'side', 'm': 'pvp'}
            jsonBtn = json.dumps(jsonData)
            inlineKb.add(InlineKeyboardButton('PvP', callback_data=jsonBtn))
            await message.answer('Выбери режим игры', reply_markup=inlineKb)
        else:
            inlineKb = keyboardBuilder(data['settings'])
            await message.answer('Выбери шаблон игры', reply_markup=inlineKb)
    else:
        await message.answer('Сервер не отвечает')
        return


async def sideCallback(callback_query: types.CallbackQuery, jsonData):
    await bot.answer_callback_query(callback_query.id)
    jsonBtn = {'cmd': 'color', 'm': jsonData['m'], 'side': 'y'}
    inlineKb = InlineKeyboardMarkup(row_width=2)
    btnData = json.dumps(jsonBtn)
    acceptBtn = InlineKeyboardButton('Да', callback_data=btnData)
    jsonBtn['side'] = 'n'
    btnData = json.dumps(jsonBtn)
    declineBtn = InlineKeyboardButton('Нет', callback_data=btnData)
    inlineKb.add(acceptBtn, declineBtn)
    await bot.edit_message_text('Учитывать смену сторон?',
                                callback_query.message.chat.id,
                                callback_query.message.message_id,
                                reply_markup=inlineKb)


async def colorCallback(callback_query: types.CallbackQuery, jsonData):
    await bot.answer_callback_query(callback_query.id)
    jsonData = {'cmd': 'enemy', 'm': jsonData['m'], 'side': jsonData['side'], 'color': 'r'}
    inlineKb = InlineKeyboardMarkup(row_width=2)
    jsonBtn = json.dumps(jsonData)
    redSideBtn = InlineKeyboardButton('Красная', callback_data=jsonBtn)
    jsonData['color'] = 'b'
    jsonBtn = json.dumps(jsonData)
    blueBtn = InlineKeyboardButton('Синяя', callback_data=jsonBtn)
    inlineKb.add(redSideBtn, blueBtn)
    await bot.edit_message_text('Выберите сторону',
                                callback_query.message.chat.id,
                                callback_query.message.message_id,
                                reply_markup=inlineKb)


async def saveSettingsToRequest(callback_query: types.CallbackQuery, jsonData):
    await bot.answer_callback_query(callback_query.id)
    template_id = saveGameSettingTemplate(callback_query, jsonData)
    data = {'id': template_id}
    if template_id:
        await chooseGamerCallback(callback_query, data)


def saveGameSettingTemplate(callback_query: types.CallbackQuery, jsonData):
    url = HOST + '/api/bot/saveGameSettings'
    requestData = {
        'chat_id': callback_query.message.chat.id,
        'mode': jsonData['m'],
        'side': jsonData['color'],
        'change': jsonData['side'],
    }
    req = requests.post(url, requestData)
    if req.status_code == 200:
        jsonData = req.json()
        if jsonData['data'] is True:
            return jsonData['id']
        return False


async def chooseGamer(message, state=None, messageEdited=False):
    postData = {'chat_id': message.chat.id}
    req = requests.post(HOST + '/api/bot/getGamers', postData)
    if req.status_code == 200:
        data = req.json()
        if len(data) == 0:
            if state:
                await state.finish()
            if messageEdited:
                await bot.edit_message_text('Сервер не отвечает',
                                            message.chat.id,
                                            message.message_id)
            else:
                await bot.send_message(message.chat.id, 'Сервер не отвечает')
        inlineKb = InlineKeyboardMarkup(row_width=1)
        for item in data:
            login = item.get('login')
            chat_id = item.get('chat_id')
            if len(login) == 0 or len(chat_id) == 0:
                continue
            btn = InlineKeyboardButton(login, callback_data=chat_id)
            inlineKb.add(btn)
        # await GameSettings.next()
        if messageEdited:
            await bot.edit_message_text('Выбери соперника',
                                        message.chat.id,
                                        message.message_id,
                                        reply_markup=inlineKb)
        else:
            await bot.send_message(message.chat.id,
                                   'Выбери соперника',
                                   reply_markup=inlineKb)
    else:
        if state:
            await state.finish()
        if messageEdited:
            await bot.edit_message_text('Сервер не отвечает',
                                        message.chat.id,
                                        message.message_id)
        else:
            await bot.send_message(message.chat.id, 'Сервер не отвечает')


async def chooseGamerCallback(callback_query: types.CallbackQuery, jsonData):
    postData = {'chat_id': callback_query.message.chat.id}
    req = requests.post(HOST + '/api/bot/getGamers', postData)
    if req.status_code == 200:
        data = req.json()
        if len(data) == 0:
            await bot.edit_message_text('Игроков не найдено',
                                        callback_query.message.chat.id,
                                        callback_query.message.message_id)
        inlineKb = InlineKeyboardMarkup(row_width=1)
        for item in data:
            login = item.get('login')
            chat_id = item.get('chat_id')
            if len(login) == 0 or len(chat_id) == 0:
                continue
            jsonData = {'cmd': 'request', 'id': jsonData['id'], 'ch_id': chat_id}
            jsonBtn = json.dumps(jsonData)
            btn = InlineKeyboardButton(login, callback_data=jsonBtn)
            inlineKb.add(btn)
            await bot.edit_message_text('Выбери соперника',
                                        callback_query.message.chat.id,
                                        callback_query.message.message_id,
                                        reply_markup=inlineKb)
    else:
        await bot.edit_message_text('Сервер не отвечает',
                                    callback_query.message.chat.id,
                                    callback_query.message.message_id)


async def requestToGamer(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    stateData = await state.get_data()
    await state.finish()
    # await sendToRecipient(callback_query, stateData['t_id'])


async def requestToGamerCallback(callback_query: types.CallbackQuery, jsonData):
    req = requests.post(HOST + '/api/bot/getGameSettingsById', {'template_id': jsonData['id']})
    if req.status_code == 200:
        data = req.json()
        if data['data'] is True:
            settings = data['settings']
            if settings['mode'] == 'pvp':
                modeGame = 'Режим: PvP \n'
            else:
                modeGame = 'Режим: TvT \n'
            if settings['side'] == 'red':
                sideGame = 'За сторону синих \n'
            else:
                sideGame = 'За сторону красных \n'
            if settings['side_change'] == 1:
                sideChange = 'Со сменой сторон \n'
            else:
                sideChange = 'Без смены сторон \n'
            fromUserName = callback_query.message.chat.first_name
            text = 'Пользователь ' + fromUserName + ' рискнул бросить тебе вызов: \n'
            text += modeGame + sideGame + sideChange

            sendData = {'cmd': 'accept', 'f': callback_query.message.chat.id, 'id': settings['id'], 'd': True}
            acceptJson = json.dumps(sendData)
            sendData['d'] = False
            declineJson = json.dumps(sendData)
            inlineKb = InlineKeyboardMarkup(row_width=2)
            acceptBtn = InlineKeyboardButton('Принять', callback_data=acceptJson)
            declineBtn = InlineKeyboardButton('Я ссыкло', callback_data=declineJson)
            inlineKb.add(acceptBtn, declineBtn)
            await bot.send_message(jsonData['ch_id'],
                                   text,
                                   reply_markup=inlineKb)
            # Ответ бросившему вызов
            await bot.edit_message_text('Ждем ответа от игрока',
                                        callback_query.message.chat.id,
                                        callback_query.message.message_id)
            return

    await bot.edit_message_text('Что то пошло не так',
                                callback_query.message.chat.id,
                                callback_query.message.message_id)


def keyboardBuilder(settings):
    inlineKb = InlineKeyboardMarkup(row_width=1)
    for item in settings:
        if item['mode'] == 'pvp':
            textBtn = 'PvP.'
        else:
            textBtn = 'TvT.'
        if item['side'] == 'red':
            textBtn += ' За красных.'
        else:
            textBtn += ' За синих.'
        if item['side_change'] == 1:
            textBtn += ' Со сменой сторон.'
        else:
            textBtn += ' Без смены сторон.'
        jsonData = {'cmd': 'template', 'id': item['id']}
        jsonBtn = json.dumps(jsonData)
        inlineBtn = InlineKeyboardButton(textBtn, callback_data=jsonBtn)
        inlineKb.add(inlineBtn)
    return inlineKb
