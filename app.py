from aiogram import Bot, Dispatcher, executor, types
from loader import dp, bot
import startHandler
import challangeHandler
import acceptChallengeHandler
import json


@dp.callback_query_handler(lambda callback_query: True)
async def callbacksHandler(callback_query: types.CallbackQuery):
    callback_data = callback_query.data
    jsonData = json.loads(callback_data)
    cmd = jsonData['cmd']
    if cmd == 'acpt':
        await acceptChallengeHandler.acceptChallengeHandler(callback_query, jsonData)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
