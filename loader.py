import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

API_TOKEN = '5579060007:AAHzg4zSJKB8M3Kl7eQiesVarE0FoqOGr3Q'
HOST = 'http://localhost'
WS_HOST = 'ws://localhost:8080'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)
