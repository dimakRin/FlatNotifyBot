import aiosqlite3 as sq
from . import redis_bot
import time


async def sql_start():
    global base,cur
    base = await sq.connect('flat_base.db')
    cur = await base.cursor()

    await base.execute('CREATE TABLE IF NOT EXISTS table_ru09(id PRIMARY KEY, link, description, price, date)')
    await base.commit()

    await base.execute('CREATE TABLE IF NOT EXISTS table_bes_pos(id PRIMARY KEY, link, description, price, date)')
    await base.commit()

    await base.execute('CREATE TABLE IF NOT EXISTS users(id PRIMARY KEY, web_site, districts, rooms, price, status)')
    await base.commit()


async def get_id_ru09():
    command = await cur.execute('SELECT id FROM table_ru09')
    return command.fetchall()


async def get_id_bespos():
    command = await cur.execute('SELECT id FROM table_bes_pos')
    return command.fetchall()


async def add_ads_ru09(dict_):
    await cur.execute("INSERT INTO table_ru09 VALUES(:id, :link,:description, :price, :date)", dict_)
    await base.commit()


async def add_ads_bespos(dict_):
    await cur.execute("INSERT INTO table_bes_pos VALUES(:id, :link,:description, :price, :date)", dict_)
    await base.commit()


async def get_users():
    command = await cur.execute('SELECT id FROM users')
    return command.fetchall()


async def update_user_items(user_id):
    all_user = await get_users()
    if not all_user:
        await cur.execute("INSERT INTO users VALUES(:id, :web_site, :districts, :rooms, :price, :status)",
                          await redis_bot.get_all_redis_items(user_id))
        await base.commit()
    elif user_id not in (user_id_fetc[0] for user_id_fetc in all_user):
        await cur.execute("INSERT INTO users VALUES(:id, :web_site, :districts, :rooms, :price, :status)",
                          await redis_bot.get_all_redis_items(user_id))
        await base.commit()
    else:
        await cur.execute("UPDATE users SET "
                          "web_site= :web_site, districts= :districts, rooms= :rooms, price= :price, status= :status"
                          " WHERE id= :id ",
                          await redis_bot.get_all_redis_items(user_id))
        await base.commit()


async def get_all_users_items():
    items = []
    command = await cur.execute('SELECT * FROM users')
    for user_items in command.fetchall():
        items.append({
            'id': user_items[0],
            'items': {
            'web-site': user_items[1],
            'districts': user_items[2],
            'rooms': user_items[3],
            'price': user_items[4],
            'status': user_items[5],
            }
        })
    return items


async def update_status(user_id):
    await cur.execute("UPDATE users SET status= ? WHERE id= ?",('01', user_id))
    await base.commit()


async def get_last_adv_ru09():
    advs_ru09=[]
    day = time.time() - 86400
    command = await cur.execute('SELECT * FROM table_ru09 WHERE date> ?', (day,))
    for adv in command.fetchall():
        advs_ru09.append({
            'link': adv[1],
            'description': adv[2],
            'price': adv[3],
        })
    return advs_ru09


async def get_last_adv_bespos():
    advs_bespos=[]
    day = time.time() - 86400
    command = await cur.execute('SELECT * FROM table_bes_pos WHERE date> ?', (day,))
    for adv in command.fetchall():
        advs_bespos.append({
            'link': adv[1],
            'description': adv[2],
            'price': adv[3],
        })
    return advs_bespos