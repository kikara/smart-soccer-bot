from loader import dp, bot
from aiogram import types
import requests
from loader import HOST

@dp.message_handler(commands="start")
async def start(message: types.Message):
    exploded = message.text.split(' ')
    if len(exploded) == 1 or len(exploded) > 2:
        await message.answer('Пожалйстка укажите токен с ЛК в формате: /start token')
        return
    postData = {
        'username': message['chat']['username'],
        'user_id': message['chat']['id'],
        'token': exploded[1]
    }
    url = HOST + '/api/bot/saveTelegramData'
    req = requests.post(url, json=postData)
    await message.answer('Вы успешно зарегистрированы')
