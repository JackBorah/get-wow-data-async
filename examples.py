import getwowdataasync
import asyncio

async def main():
    us_api = await getwowdataasync.WowApi.create('us') #region
    winterhoof_auctions = await us_api.get_auctions(4) #4 = Winterhoof's connected realm id
    await us_api.close() #close aiohttp session after queries are done

    total_value = 0
    for item in winterhoof_auctions['auctions']:
        if item.get('unit_price'):
            total_value += item.get('unit_price')
        elif item.get('buyout'):
            total_value += item.get('buyout')
        elif item.get('bid'):
            total_value += item.get('bid')

    print(getwowdataasync.as_gold(total_value))
    #prints 430,846,968g 67s 00c

from pprint import pprint
from getwowdataasync import WowApi

async def main():
    eu_api = await WowApi.create('eu')
    params = {"name.en_US":"Thunderfury"}

    result_item = await eu_api.item_search(**params)
    await eu_api.close()
    pprint(result_item)
    #prints json containing all items with the name Thunderfury. 


from pprint import pprint
from getwowdataasync import WowApi

async def main():
    us_api = await WowApi.create('us')
    wow_token_data = await us_api.get_wow_token()
    await us_api.close()

    pprint(wow_token_data)
    #prints:
    # {'_links': {'self': {'href': 'https://us.api.blizzard.com/data/wow/token/?namespace=dynamic-us'}},
    # 'last_updated_timestamp': 1653847530000,
    # 'price': 1656890000} 

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main())