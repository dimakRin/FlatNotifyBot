from create_bot import dp
from aiogram.utils import executor
from database import sqllite_bot as sq
from database import redis_bot
from setting_filter import startup_filter_handlers
from adv_processing import handlers_adv
import asyncio


async def on_startup(_):
    await sq.sql_start()
    for user_items in await sq.get_all_users_items():
        await redis_bot.loading_user(user_items)


startup_filter_handlers.register_handlers_choice_filter(dp)
handlers_adv.register_handlers_adv(dp)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(handlers_adv.flat_notify())

    executor.start_polling(dp, skip_updates=False, on_startup=on_startup)
