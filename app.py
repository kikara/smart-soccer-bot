from aiogram import Bot, Dispatcher, executor, types
from loader import dp, bot
import startHandler
import challangeHandler
import acceptChallengeHandler
import json


@dp.callback_query_handler(lambda callback_query: True)
async def callbacksHandler(callback_query: types.CallbackQuery):
    callback_data = callback_query.data
    exploded = callback_data.split('=')
    cmd = exploded[0]
    data = exploded[1]
    if cmd == 'acpt':
        await acceptChallengeHandler.acceptChallengeHandler(callback_query, data)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
