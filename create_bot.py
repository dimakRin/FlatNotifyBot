from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from config import TOKEN
storage = RedisStorage2()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)