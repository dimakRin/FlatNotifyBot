from aiogram import types
from database import redis_bot
from config import districts, web_sites, rooms, user_items
from . import exceptions


def get_result_filter(mask, dict):
    count = 0
    result = []

    for _, value in dict.items():
        if mask[count] == '1':
            result.append(value)
        count += 1

    return result


async def get_setting_message(callback: types.CallbackQuery):
    return ('Текушие параметры поиска: \n\n'
            '<b>Сайты: </b>' + ', '.join(get_result_filter(
        await redis_bot.get_redis_items(callback.from_user.id, list(user_items.keys())[0]), web_sites))+'\n\n'
            '<b>Районы: </b>' + ', '.join(get_result_filter(
        await redis_bot.get_redis_items(callback.from_user.id, list(user_items.keys())[1]), districts)) + '\n\n'
            '<b>Количество комнат: </b>' + ', '.join(get_result_filter(
        await redis_bot.get_redis_items(callback.from_user.id, list(user_items.keys())[2]), rooms)) + '\n\n'
            '<b>Стоимость: </b>' +
            ('не имеет значения' if await redis_bot.get_redis_items(callback.from_user.id, list(user_items.keys())[3])=='0'
             else await redis_bot.get_redis_items(callback.from_user.id, list(user_items.keys())[3])) + '\n\n'

    )


def exceptions_price(message: types.Message):
    try:
        if '-' not in message.text:
            raise exceptions.WithoutDash
        if int(message.text.split('-')[0]) >= int(message.text.split('-')[1]):
            raise exceptions.WrongOrder
        return {
            'except': 0
        }
    except exceptions.WithoutDash:
        return {
            'except': 1,
            'text': '⚠ Пожалуйста поставьте между минимальной и максимальной ценной:-\n\n'
        }
    except exceptions.WrongOrder:
        return {
            'except': 1,
            'text': '⚠ Минимальная цена не может равняться или быть больше максимальной, попробуйте еще раз:\n\n'
        }
    except ValueError:
        return {
            'except': 1,
            'text': '⚠ Извините, вы можете вводить только целые числа, попробуйте еще раз:\n\n'
        }