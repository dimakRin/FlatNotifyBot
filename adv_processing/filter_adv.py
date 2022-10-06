from database import redis_bot as rb

def f_district(text, check):
    dist = {
        1: 'Кировск',
        2: 'Советск',
        3: 'Ленинск',
        4: 'Окятборск'
    }
    count=1
    for status in check:
        if status == '1':
            if dist[count] in text:
                return True
            count += 1
        else:
            count += 1
    return False


def f_rooms(text, check):
    count=0
    for status in check:
        if status == '1' and count == 0:
            if (' комнат' in text) or ('Комната' in text) or ('Студия' in text):
                return True
        if status == '1':
            if (str(count) + '-ком') in text:
                return True
        count += 1
    return False


def f_price(text, price):
    if price != '0':
        if (int(text) >= (int(price.split('-')[0])*1000)) and (int(text) <= (int(price.split('-')[1])*1000)):
            return True
        else:
            return False
    else:
        return True


async def filter_ru09(user_id, dict_adv):
    desc = dict_adv['description'][: dict_adv['description'].find('районе')]
    if (f_district(desc, await rb.get_redis_items(int(user_id), 'districts')) and
            f_rooms(desc, await rb.get_redis_items(int(user_id), 'rooms')) and
            f_price(str(dict_adv['price']), await rb.get_redis_items(int(user_id), 'price'))):
        return True
    return False


async def filter_bespos(user_id, dict_adv):
    desc = dict_adv['description'][: dict_adv['description'].find('р-н')]
    if (f_district(desc, await rb.get_redis_items(int(user_id), 'districts')) and
            f_rooms(dict_adv['description'], await rb.get_redis_items(int(user_id), 'rooms')) and
            f_price(str(dict_adv['price']), await rb.get_redis_items(int(user_id), 'price'))):
        return True
    return False


#нужно ли данному пользователю производить проверку по сайту: ru09?
async def ru09_is_enable(user_id):
    if (await rb.get_status_sheach(int(user_id)) == '1') and (
            await rb.get_user_web(int(user_id), 'ru09') == '1'):
        return True
    else:
        return False


#нужно ли данному пользователю производить проверку по сайту: безпосредника?
async def bespos_is_enable(user_id):
    if (await rb.get_status_sheach(int(user_id)) == '1') and (
            await rb.get_user_web(int(user_id), 'bespos') == '1'):
        return True
    else:
        return False



