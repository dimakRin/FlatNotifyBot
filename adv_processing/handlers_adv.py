from create_bot import bot
from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from . import filter_adv
from . import parsing_adv
from database import redis_bot
from database import sqllite_bot as sq
from setting_filter.support_functions import get_setting_message
import asyncio

button_back = InlineKeyboardButton(text='↩ Вернуться к настройкам',
                                                                    callback_data='back')
button_back_from_adv = InlineKeyboardButton(text='↩ Вернуться к настройкам',
                                                                    callback_data='back_from_adv')
button_last = InlineKeyboardButton(text='⬇ Показать объявления за последние сутки',
                                                                    callback_data='last')
inl_start = InlineKeyboardMarkup(row_width=1).add(button_last).add(button_back)
inl_back = InlineKeyboardMarkup(row_width=1).add(button_back_from_adv)


def message_adv(dict_):
    return ("<b>Описание:</b> " + dict_['description'] + "\n"
            "<b>Цена:</b> " + dict_['price'] + "\n"
            "<b>Ссылка:</b> " + dict_['link'] + "\n")


async def notify_register(callback: types.callback_query):
    await redis_bot.set_status_sheach(callback)
    await sq.update_user_items(callback.from_user.id)
    await bot.edit_message_text(await get_setting_message(callback), callback.from_user.id,
                                callback.message.message_id, reply_markup=inl_start,
                                parse_mode='html')
    await callback.answer()


async def get_last_adv(callback: types.callback_query):
    if await filter_adv.ru09_is_enable(callback.from_user.id):
        for adv in await sq.get_last_adv_ru09():
            if await filter_adv.filter_ru09(callback.from_user.id, adv):
                await bot.send_message(int(callback.from_user.id), message_adv(adv), parse_mode='html',
                                       reply_markup=inl_back)

    if await filter_adv.bespos_is_enable(callback.from_user.id):
        for adv in await sq.get_last_adv_bespos():
            if await filter_adv.filter_bespos(callback.from_user.id, adv):
                await bot.send_message(int(callback.from_user.id), message_adv(adv), parse_mode='html',
                                       reply_markup=inl_back)



async def flat_notify():
    while True:
        bes = await parsing_adv.get_advertisment_bespos()
        ru = await parsing_adv.get_advertisment_ru09()
        for adv in bes:
            await sq.add_ads_bespos(adv)
        for adv in ru:
            await sq.add_ads_ru09(adv)

        if ru:
            for user_id in await redis_bot.get_users_id():
                if await filter_adv.ru09_is_enable(user_id):
                    for adv in ru:
                        if await filter_adv.filter_ru09(user_id, adv):
                            await bot.send_message(int(user_id), message_adv(adv), parse_mode='html',
                                                   reply_markup=inl_back)

        if bes:
            for user_id in await redis_bot.get_users_id():
                if await filter_adv.bespos_is_enable(user_id):
                    for adv in bes:
                        if await filter_adv.filter_bespos(user_id, adv):
                            await bot.send_message(int(user_id), message_adv(adv), parse_mode='html',
                                                   reply_markup=inl_back)

        await asyncio.sleep(30)



def register_handlers_adv(dp: Dispatcher):
    dp.register_callback_query_handler(notify_register, text='start_search')
    dp.register_callback_query_handler(get_last_adv, text='last')