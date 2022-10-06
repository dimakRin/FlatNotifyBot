import aiohttp
from bs4 import BeautifulSoup
import time
from config import LINKS
from database import sqllite_bot as sq


async def get_advertisment_ru09():
    list_adv = []
    async with aiohttp.ClientSession() as session:
        response_ru09 = await session.get(LINKS['ru09'])
        soup_ru09 = BeautifulSoup(await response_ru09.text(), 'html.parser')
        all_ads_ru09 = soup_ru09.find_all('td', class_='first last')
        time_ads_ru09 = time.time()

        for advertisment in all_ads_ru09:
            id_ru09 = advertisment.find('div').get('id')
            if id_ru09 not in (id_gen[0] for id_gen in await sq.get_id_ru09()):
                list_adv.append({ 'id' : id_ru09,
                        'link': 'https://m.tomsk.ru09.ru/' + advertisment.find('a', class_='visited_ads').get('href'),
                        'description':  advertisment.find('p').text + advertisment.find_all('p')[1].text.partition('Есть')[0],
                        'price': "".join(advertisment.find('div', class_='inline').get_text(strip=True).split()).replace('руб.', ''),
                        'date': int(time_ads_ru09)
                  })
        return list_adv

async def get_advertisment_bespos():
    list_adv=[]
    async with aiohttp.ClientSession() as session:
        response_bespos = await session.get(LINKS['bes_pos'])
        soup_bespos=BeautifulSoup(await response_bespos.text(),'html.parser')
        all_ads_bespos=soup_bespos.find_all('div', class_='sEnLiCell unavailable')
        time_ads_bespos = time.time()

        for advertisment in all_ads_bespos:
            id_bespos = advertisment.get('data-id')
            if id_bespos not in (id_gen[0] for id_gen in await sq.get_id_bespos()):
                list_adv.append({ 'id' : id_bespos,
                      'link' : advertisment.find('link').get('href'),
                      'description' : advertisment.find('div', class_='sEnLiCity').get_text(strip = True) + '\n'+ advertisment.find('div', class_='sEnLiTitle').get_text(strip = True) ,
                      'price' : advertisment.find('div', class_='sEnLiPrice').find('span').get('content'),
                      'date': int(time_ads_bespos)
                      })
        return list_adv