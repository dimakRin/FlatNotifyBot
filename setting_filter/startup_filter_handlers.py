from create_bot import dp, bot
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .inline_checkbox import InlineCheckBox
from config import districts, web_sites, rooms, user_items
from .support_functions import get_setting_message,exceptions_price
from database import redis_bot
from database import sqllite_bot as sq

accept_dist = 'accept_dist'
accept_web  = 'accept_web'
accept_room = 'accept_room'
accept_price= 'accept_price'


class States(StatesGroup):
    price = State()


inl_checkbox_dist = InlineCheckBox(districts, accept_callback=accept_dist)
inl_checkbox_web = InlineCheckBox(web_sites, accept_callback=accept_web)
inl_checkbox_room = InlineCheckBox(rooms, accept_callback=accept_room)
# Кнопка начала поиска:
inl_startup = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='⚙ Настроить критерии поиска', callback_data='startup'))
# Кнопки для фильтра цен:
inl_price = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='🤑 Не имеет значения', callback_data=accept_price))
inl_menu = InlineKeyboardMarkup(row_width=1)\
    .add(InlineKeyboardButton(text='💬 Изменить выбраные сайты ', callback_data='web'))\
    .add(InlineKeyboardButton(text='🏘 Изменить выбранные районы', callback_data='dist'))\
    .add(InlineKeyboardButton(text='🛌 Изменить количество комнат', callback_data='room'))\
    .add(InlineKeyboardButton(text='💲 Изменить цену', callback_data='price'))\
    .add(InlineKeyboardButton(text='🔍 Начать поиск', callback_data='start_search'))


price_text=('На какую сумму в месяц вы можете рассчитывать?\n\n'
            'Введите минимальную и максимальную цену в тысячах рублей в виде: мин.цена-макс.цена.\n\n'
            '<b>Пример сообщения:</b>\n'
            '10-25')


async def start_registration(message: types.Message ):
    await bot.send_message(message.from_user.id,'👋 Перед началом работы, давайте определимся с критериями поиска',
                                 reply_markup=inl_startup)
    await redis_bot.new_user(message)
    await redis_bot.set_status_check(message, '0')



async def start_choice(callback: types.callback_query):
    await bot.edit_message_text('💬 Выберете сайты:', callback.from_user.id, callback.message.message_id,
                                 reply_markup=inl_checkbox_web)
    await callback.answer()


async def choice_site_callback(callback: types.callback_query):
    if callback.data == 'web':
        await bot.edit_message_text('💬 Выберете сайты:', callback.from_user.id, callback.message.message_id,
                                    reply_markup=inl_checkbox_web.buttons_fill_callback(callback,
                                                    chek=await redis_bot.get_redis_items(callback.from_user.id,list(user_items.keys())[0])))
        await callback.answer()
    else:
        await bot.edit_message_text('💬 Выберете сайты:', callback.from_user.id, callback.message.message_id,
                                     reply_markup=inl_checkbox_web.buttons_fill_callback(callback))
        await callback.answer()


async def choice_site_accept(callback: types.callback_query):
    await redis_bot.update_redis_items(callback, list(user_items.keys())[0], inl_checkbox_web.get_result(callback))
    if await redis_bot.get_status_check(callback) == '0':
        await bot.edit_message_text('🏘 Выберете районы:', callback.from_user.id, callback.message.message_id,
                                                                reply_markup=inl_checkbox_dist)
        await callback.answer()
    else:
        await bot.edit_message_text(await get_setting_message(callback), callback.from_user.id,
                                    callback.message.message_id,
                                    reply_markup=inl_menu, parse_mode='html')
        await callback.answer()


async def choice_district_callback(callback: types.callback_query):
    if callback.data == 'dist':
        await bot.edit_message_text('🏘 Выберете районы:', callback.from_user.id, callback.message.message_id,
                                    reply_markup=inl_checkbox_dist.buttons_fill_callback(callback,
                                        chek=await redis_bot.get_redis_items(callback.from_user.id, list(user_items.keys())[1])))
        await callback.answer()
    else:
        await bot.edit_message_text('🏘 Выберете районы:', callback.from_user.id, callback.message.message_id,
                                    reply_markup=inl_checkbox_dist.buttons_fill_callback(callback))
        await callback.answer()


async def choice_district_accept(callback: types.callback_query):
    await redis_bot.update_redis_items(callback, list(user_items.keys())[1], inl_checkbox_dist.get_result(callback))
    if await redis_bot.get_status_check(callback) == '0':
        await bot.edit_message_text('🛌 Выберете количество комнат:', callback.from_user.id, callback.message.message_id,
                                                                reply_markup=inl_checkbox_room)
        await callback.answer()
    else:
        await bot.edit_message_text(await get_setting_message(callback), callback.from_user.id,
                                    callback.message.message_id,
                                    reply_markup=inl_menu, parse_mode='html')
        await callback.answer()


async def choice_room_callback(callback: types.callback_query):
    if callback.data == 'room':
        await bot.edit_message_text('🛌 Выберете количество комнат:', callback.from_user.id,
                                    callback.message.message_id,
                                    reply_markup=inl_checkbox_room.buttons_fill_callback(callback,
                                                                                         chek=await redis_bot.get_redis_items(callback.from_user.id, list(user_items.keys())[2])))
        await callback.answer()
    else:
        await bot.edit_message_text('🛌 Выберете количество комнат:', callback.from_user.id, callback.message.message_id,
                                    reply_markup=inl_checkbox_room.buttons_fill_callback(callback))
        await callback.answer()


async def choice_room_accept(callback: types.callback_query, state: FSMContext):
    await redis_bot.update_redis_items(callback, list(user_items.keys())[2], inl_checkbox_room.get_result(callback))
    if await redis_bot.get_status_check(callback) == '0':
        async with state.proxy() as data:
            data['price']=callback.message.message_id
        await States.price.set()
        await bot.edit_message_text(price_text, callback.from_user.id, callback.message.message_id,
                                 reply_markup=inl_price,parse_mode='html')
        await callback.answer()
    else:
        await bot.edit_message_text(await get_setting_message(callback), callback.from_user.id,
                                    callback.message.message_id,
                                    reply_markup=inl_menu, parse_mode='html')
        await callback.answer()


async def choice_price(callback : types.CallbackQuery,  state: FSMContext):
    async with state.proxy() as data:
        data['price'] = callback.message.message_id
    await States.price.set()
    await bot.edit_message_text(price_text, callback.from_user.id, callback.message.message_id,
                                reply_markup=inl_price,parse_mode='html')
    await callback.answer()


async def choice_price_enter(message: types.Message, state: FSMContext):
    if exceptions_price(message)['except'] == 0:
        async with state.proxy() as data:
            await redis_bot.update_redis_items(message, list(user_items.keys())[3], message.text)
            await bot.edit_message_text(await get_setting_message(message), message.from_user.id,
                                        data['price'],
                                        reply_markup=inl_menu, parse_mode='html')
        await redis_bot.update_redis_items(message, list(user_items.keys())[3], message.text)
        await redis_bot.set_status_check(message)
        await state.finish()
    else:
        try:
            async with state.proxy() as data:
                await bot.edit_message_text(exceptions_price(message)['text']+price_text, message.from_user.id, data['price'],
                                            reply_markup=inl_price,parse_mode='html')
        except:
            pass
    await message.delete()


async def choice_price_accept(callback: types.callback_query,state: FSMContext):
    await redis_bot.update_redis_items(callback, list(user_items.keys())[3],'0')
    await bot.edit_message_text(await get_setting_message(callback), callback.from_user.id, callback.message.message_id,
                                 reply_markup=inl_menu, parse_mode='html')
    await callback.answer()
    await redis_bot.set_status_check(callback)
    await state.finish()


async def back_to_setting(callback: types.callback_query):
    await redis_bot.set_status_sheach(callback,'0')
    await sq.update_status(callback.from_user.id)
    await bot.edit_message_text(await get_setting_message(callback), callback.from_user.id, callback.message.message_id,
                                reply_markup=inl_menu, parse_mode='html')
    await callback.answer()


async def back_to_setting_from_adv(callback: types.callback_query):
    await redis_bot.set_status_sheach(callback,'0')
    await sq.update_status(callback.from_user.id)
    await bot.send_message(callback.from_user.id, await get_setting_message(callback),
                                reply_markup=inl_menu, parse_mode='html')
    await callback.answer()


def register_handlers_choice_filter(dp: Dispatcher):
    dp.register_message_handler(start_registration, commands=['start'])
    dp.register_callback_query_handler(start_choice, text='startup')
    dp.register_callback_query_handler(choice_site_callback, text=[*web_sites,'web'])
    dp.register_callback_query_handler(choice_site_accept, text=accept_web)
    dp.register_callback_query_handler(choice_district_callback, text=[*districts,'dist'])
    dp.register_callback_query_handler(choice_district_accept, text=accept_dist)
    dp.register_callback_query_handler(choice_room_callback, text=[*rooms,'room'])
    dp.register_callback_query_handler(choice_room_accept, text=accept_room)
    dp.register_callback_query_handler(choice_price, text='price')
    dp.register_callback_query_handler(choice_price_accept, text=accept_price, state=States.price)
    dp.register_message_handler(choice_price_enter, state=States.price)
    dp.register_callback_query_handler(back_to_setting, text='back')
    dp.register_callback_query_handler(back_to_setting_from_adv, text='back_from_adv')
