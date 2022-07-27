from aiogram import Bot, Dispatcher, executor, types
from loader import dp, bot
import startHandler
import challangeHandler
import json

@dp.callback_query_handler(lambda callback_query: True)
async def allCallbackQueries(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    exploded = callback_query.data.split('=')
    choice = exploded[0]
    jsonData = json.loads(exploded[1])
    print(choice)
    print(jsonData)
    text = 'Пользователь не отвечает'
    textToSender = ''
    if choice == 'a':
        text = 'Вызов принят'
        textToSender = 'Наконец-то достойный противник'
    if choice == 'd':
        text = 'Он признал себя ссыклом'
        textToSender = 'Достаточно крысиный поступок'
    await bot.send_message(
            jsonData['f'],
            text)
    await bot.edit_message_text(textToSender,
                          callback_query.message.chat.id,
                          callback_query.message.message_id)
#     TODO query to server about start game


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
