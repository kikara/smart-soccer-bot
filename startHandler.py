from loader import dp, bot
from aiogram import types
import requests
from loader import HOST


@dp.message_handler(commands="start")
async def start(message: types.Message):
    exploded = message.text.split(' ')

    if len(exploded) == 1 or len(exploded) > 2:
        await message.answer('Пожалуйста укажите токен с ЛК в формате: /start token')
        return
    data = {
        'username': message['chat']['username'],
        'user_id': message['chat']['id'],
        'token': exploded[1]
    }

    url = HOST + '/api/users/' + str(data['user_id']) + '/telegrams'

    req = requests.patch(url, json=data)

    if req.status_code == 200:
        await message.answer('Вы успешно зарегистрированы')
