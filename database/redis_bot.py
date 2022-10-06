import aioredis as redis
from config import user_items


async def new_user(callback):
    async with redis.Redis() as redis_client:
        await redis_client.hmset(str(callback.from_user.id), user_items)


async def update_redis_items(callback, name_item, item):
    async with redis.Redis() as redis_client:
        await redis_client.hset(str(callback.from_user.id), name_item, ''.join(item))


async def get_status_check(callback):
    async with redis.Redis() as redis_client:
        status = await redis_client.hget(str(callback.from_user.id), 'status')
        return str(status, 'UTF=8')[1]


async def set_status_check(callback, status='1'):
    async with redis.Redis() as redis_client:
        await redis_client.hset(str(callback.from_user.id), 'status', await get_status_sheach(callback.from_user.id) + status)


async def get_status_sheach(user_id):
    async with redis.Redis() as redis_client:
        status = await redis_client.hget(str(user_id), 'status')
        return str(status, 'UTF=8')[0]


async def set_status_sheach(callback, status='1'):
    async with redis.Redis() as redis_client:
        await redis_client.hset(str(callback.from_user.id), 'status', status + await get_status_check(callback))


async def get_redis_items(user_id, name_item):
    async with redis.Redis() as redis_client:
        item = await redis_client.hget(str(user_id), name_item)
        return str(item,'UTF=8')


async def get_users_id():
    async with redis.Redis() as redis_client:
        keys = await redis_client.keys()
        return keys


async def get_user_web(user_id,site):
    web_site={
        'ru09': 0,
        'bespos': 1
    }
    async with redis.Redis() as redis_client:
        item = await redis_client.hget(str(user_id), 'web-site')
        return str(item, 'UTF=8')[web_site[site]]


async def get_all_redis_items(user_id):
    async with redis.Redis() as redis_client:
        items = await redis_client.hmget(str(user_id), 'web-site', 'districts', 'rooms', 'price', 'status')
        return {
            'id': user_id,
            'web_site': str(items[0],'UTF-8'),
            'districts': str(items[1],'UTF-8'),
            'rooms': str(items[2], 'UTF-8'),
            'price': str(items[3], 'UTF-8'),
            'status': str(items[4], 'UTF-8')
        }


async def loading_user(user_items):
    if user_items:
        async with redis.Redis() as redis_client:
            await redis_client.hmset(str(user_items['id']), user_items['items'])