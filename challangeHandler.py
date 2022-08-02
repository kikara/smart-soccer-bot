from loader import dp, bot
from aiogram import types
import requests
from loader import HOST, WS_HOST
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
import json
from acceptChallengeHandler import AcceptChallenge
from websockets import connect

class GameSettings(StatesGroup):
    side = State()
    isSideChanged = State()
    chooseGamer = State()
    finishState = State()


@dp.message_handler(commands="challenge")
async def toChallenge(message: types.Message):
    req = requests.post(HOST + '/api/bot/checkUser', {'chat_id': message.chat.id})
    if req.status_code == 200:
        data = req.json()
        if data['data'] is False:
            await message.answer('Пожалуйста сначала зарегистрируйтесь')
            return
    else:
        await message.answer('Сервер не отвечает')
        return

    req = requests.post(HOST + '/api/bot/getGameSettings', {'chat_id': message.chat.id})
    if req.status_code == 200:
        data = req.json()
        if data['data'] is True:
            await GameSettings.chooseGamer.set()
            await chooseGamer(message)
        else:
            inlineKb = InlineKeyboardMarkup(row_width=2)
            pvpBtn = InlineKeyboardButton('PvP', callback_data='pvp')
            # tvtBtn = InlineKeyboardButton('TvT', callback_data='t')
            inlineKb.add(pvpBtn)
            await GameSettings.side.set()
            await message.answer('Выберите режим игры', reply_markup=inlineKb)
    else:
        await message.answer('Сервер не отвечает')


@dp.callback_query_handler(lambda callback_query: True, state=GameSettings.side)
async def setSide(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await state.update_data(mode=callback_query.data)
    inlineKb = InlineKeyboardMarkup(row_width=2)
    redSideBtn = InlineKeyboardButton('Красная', callback_data='r')
    blueBtn = InlineKeyboardButton('Синяя', callback_data='b')
    inlineKb.add(redSideBtn, blueBtn)
    await GameSettings.next()
    await bot.edit_message_text('Выберите сторону',
                                callback_query.message.chat.id,
                                callback_query.message.message_id,
                                reply_markup=inlineKb)


@dp.callback_query_handler(lambda callback_query: True, state=GameSettings.isSideChanged)
async def setSideChanged(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await state.update_data(side=callback_query.data)
    inlineKb = InlineKeyboardMarkup(row_width=2)
    acceptBtn = InlineKeyboardButton('Да', callback_data='y')
    declineBtn = InlineKeyboardButton('Нет', callback_data='n')
    inlineKb.add(acceptBtn, declineBtn)
    await GameSettings.next()
    await bot.edit_message_text('Учитывать смену сторон?',
                                callback_query.message.chat.id,
                                callback_query.message.message_id,
                                reply_markup=inlineKb)


@dp.callback_query_handler(lambda callback_query: True, state=GameSettings.chooseGamer)
async def chooseGamerHandler(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await state.update_data(change=callback_query.data)
    await saveGameSettingTemplate(callback_query.message, state)
    await chooseGamer(callback_query.message, state, True)


async def saveGameSettingTemplate(message, state):
    url = HOST + '/api/bot/saveGameSettings'
    gameSettings = await state.get_data()
    gameSettings['chat_id'] = message.chat.id
    req = requests.post(url, gameSettings)
    # if req.status_code == 200:
    #     data = req.json()
    #     if data['data'] is True:
    #         await bot.send_message(message.chat.id, 'Настройки сохранены')
    #         return
    # await bot.send_message(message.chat.id, 'Что то пошло не так: Настройки не сохранились')


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
            btn = InlineKeyboardButton(login, callback_data=chat_id)
            inlineKb.add(btn)
        await GameSettings.next()
        if messageEdited:
            await bot.edit_message_text('Вибери соперника',
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


@dp.callback_query_handler(lambda callback_query: True, state=GameSettings.finishState)
async def requestToGamer(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await state.finish()
    await sendToRecipient(callback_query)


async def sendToRecipient(callback_query):
    req = requests.post(HOST + '/api/bot/getGameSettings', {'chat_id': callback_query.message.chat.id})
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
            fromUserName = callback_query.message.chat.first_name + ' ' + callback_query.message.chat.last_name
            text = 'Пользователь ' + fromUserName + ' рискнул бросить тебе вызов: \n'
            text += modeGame + sideGame + sideChange

            jsonData = {'f': callback_query.message.chat.id, 't_id': settings['id'], 'd': True}
            acceptJson = 'acpt=' + json.dumps(jsonData)
            jsonData['d'] = False
            declineJson = 'acpt=' + json.dumps(jsonData)
            inlineKb = InlineKeyboardMarkup(row_width=2)
            acceptBtn = InlineKeyboardButton('Принять', callback_data=acceptJson)
            declineBtn = InlineKeyboardButton('Я ссыкло', callback_data=declineJson)
            inlineKb.add(acceptBtn, declineBtn)
            await bot.send_message(callback_query.data,
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
