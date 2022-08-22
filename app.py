from aiogram import Bot, Dispatcher, executor, types
from loader import dp, bot
import startHandler
import challangeHandler
import acceptChallengeHandler
import json

callbacks = {
    'side': challangeHandler.sideCallback,
    'color': challangeHandler.colorCallback,
    'enemy': challangeHandler.saveSettingsToRequest,
    'template': challangeHandler.chooseGamerCallback,
    'request': challangeHandler.requestToGamerCallback,
    'accept': acceptChallengeHandler.acceptChallengeHandler,
    'start': acceptChallengeHandler.startGame
}


@dp.callback_query_handler(lambda callback_query: True)
async def callbacksHandler(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    callback_data = callback_query.data
    jsonData = json.loads(callback_data)
    callback = callbacks.get(jsonData['cmd'])
    if callback:
        await callback(callback_query, jsonData)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
