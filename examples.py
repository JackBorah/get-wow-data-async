import getwowdata
import asyncio

async def main():
    us_api = await getwowdata.WowApi.create('us') #region
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

    print(getwowdata.as_gold(total_value))
    #prints 430,846,968g 67s 00c

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main())
