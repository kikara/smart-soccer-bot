from loader import dp, bot
from aiogram import types
import requests
from loader import HOST
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
import json

class GameSettings(StatesGroup):
    side = State()
    isSideChanged = State()
    chooseGamer = State()
    finishState = State()


@dp.message_handler(commands="challenge")
async def toChallenge(message: types.Message):
    inlineKb = InlineKeyboardMarkup(row_width=2)
    pvpBtn = InlineKeyboardButton('PVP', callback_data='p')
    tvtBtn = InlineKeyboardButton('TvT', callback_data='t')
    inlineKb.add(pvpBtn, tvtBtn)
    await GameSettings.side.set()
    await message.answer('Выберите режим игры', reply_markup=inlineKb)


@dp.callback_query_handler(lambda callback_query: True, state=GameSettings.side)
async def setSide(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await state.update_data(m=callback_query.data)
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
    await state.update_data(s=callback_query.data)
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
async def chooseGamer(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await state.update_data(c=callback_query.data)
    postData = {'chat_id': callback_query.message.chat.id}
    req = requests.post(HOST + '/api/bot/getGamers', postData)
    if req.status_code == 200:
        data = req.json()
        if len(data) == 0:
            await state.finish()
            await bot.edit_message_text('Сервер не отвечает',
                                        callback_query.message.chat.id,
                                        callback_query.message.message_id)
        inlineKb = InlineKeyboardMarkup(row_width=1)
        for item in data:
            login = item.get('login')
            chat_id = item.get('chat_id')
            btn = InlineKeyboardButton(login, callback_data=chat_id)
            inlineKb.add(btn)
        await GameSettings.next()
        await bot.edit_message_text('Виберите соперника',
                                    callback_query.message.chat.id,
                                    callback_query.message.message_id,
                                    reply_markup=inlineKb)
    else:
        await state.finish()
        await bot.edit_message_text('Сервер не отвечает',
                                    callback_query.message.chat.id,
                                    callback_query.message.message_id)



@dp.callback_query_handler(lambda callback_query: True, state=GameSettings.finishState)
async def requestToGamer(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    gameSettings = await state.get_data()
    gameSettings['f'] = callback_query.message.chat.id
    await state.finish()
    fromUserName = callback_query.message.chat.first_name + ' ' + callback_query.message.chat.last_name
    # Вызов на бой - отправить ему сообщение

    jsonData = json.dumps(gameSettings)
    inlineKb = InlineKeyboardMarkup(row_width=2)
    acceptData = 'a=' + jsonData
    declineData = 'd=' + jsonData
    acceptBtn = InlineKeyboardButton('Принять', callback_data=acceptData)
    declineBtn = InlineKeyboardButton('Я ссыкло', callback_data=declineData)
    inlineKb.add(acceptBtn, declineBtn)
    await bot.send_message(callback_query.data,
                           'Пользователь ' + fromUserName + ' рискнул бросить тебе вызов',
                           reply_markup=inlineKb)
    # Ответ бросившему вызов
    await bot.edit_message_text('Ждем ответа от игрока',
                                callback_query.message.chat.id,
                                callback_query.message.message_id)
