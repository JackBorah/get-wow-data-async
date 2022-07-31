import asyncio
import os
import time

import aiohttp
from dotenv import load_dotenv

from getwowdata.urls import urls
from getwowdata.helpers import *

class WowApi():
    
    @classmethod
    async def create(cls, region):
        self = WowApi() 
        self.region = region 
        timeout = aiohttp.ClientTimeout(connect=1, sock_read=60, sock_connect=1)
        self.session = aiohttp.ClientSession(raise_for_status=True, timeout=timeout)   
        await self.get_access_token()   
        return self 


    async def get_access_token(self, wow_api_id: str = None, wow_api_secret: str = None, retries: int = 5) -> None:
        load_dotenv()
        id = os.environ["wow_api_id"]
        secret = os.environ["wow_api_secret"]
        token_data = {"grant_type": "client_credentials"}
        wow_api_id = wow_api_id
        wow_api_secret = wow_api_secret

        for retry in range(retries):
            try:
                async with self.session.post(urls['access_token'].format(region=self.region), auth=aiohttp.BasicAuth(id, secret), data=token_data) as response:
                    response = await response.json()
                    self.access_token = response['access_token']
            except aiohttp.ClientConnectionError as e: 
                print(f'access token {e}')          
            except aiohttp.ClientResponseError as e:
                print(f'access token {e.status}')


    async def _fetch_get(self, url_name: str, ids: dict = None, retries: int = 5):
        params = {
            **{
                "access_token": self.access_token,
                "namespace": f"dynamic-{self.region}",
            },

        }
        for retry in range(retries):
            try:
                async with self.session.get(urls[url_name].format(region=self.region, **ids), params=params) as response:
                    if url_name == 'repice_icon' or 'profession_icon' or 'item_icon':
                        return await response.read()
                    else:
                        json = await response.json()
                        json['Date'] = response.headers['Date']
                        return json
            except aiohttp.ClientConnectionError as e: 
                print(f'get {e}')          
            except aiohttp.ClientResponseError as e:
                print(f'get {e.status}')


    async def _fetch_search(self, url_name: str, extra_params: dict, retries: int = 5):
        params = {
                "access_token": self.access_token,
                "namespace": f"static-{self.region}",
            }

        search_params = {
            **params,
            **extra_params,
        }

        for retry in range(retries):
            try:
                async with self.session.get(urls[url_name], params=search_params) as response:
                    json = await response.json()
                    if url_name == 'search_item':
                        tasks = []
                        if json.get('results'):
                            for item in json['results']:
                                task = asyncio.create_task(self._get_item(item['key']['href'], params=params))
                                tasks.append(task)
                        items = await asyncio.gather(*tasks)
                        json = {}
                        json['items'] = items
                    json['Date'] = response.headers['Date']
                    return json

            except aiohttp.ClientConnectionError as e: 
                print(f'search {e}')          
            except aiohttp.ClientResponseError as e:
                print(f'search {e.status}')


    async def _get_item(self, url: str, params: dict) -> dict:
        for retry in range(5):
            try:
                async with self.session.get(url, params=params) as item_data:
                    item = await item_data.json(content_type=None)
                    return item
            except aiohttp.ClientConnectionError as e: 
                print(f'item {e}')  
            except aiohttp.ClientResponseError as e:
                print(e.status)


    async def connected_realm_search(self, **extra_params: dict) -> dict:
        url_name = 'search_realm'
        return await self._fetch_search(url_name, extra_params=extra_params)


    async def item_search(self, **extra_params: dict) -> dict:
        url_name = 'search_item'
        return await self._fetch_search(url_name, extra_params=extra_params)

    async def get_connected_realms_by_id(
        self, connected_realm_id: int
    ) -> dict:
        url_name = 'realm'
        ids = {'connected_realm_id':connected_realm_id}
        return await self._fetch_get(url_name, ids)

    async def get_auctions(self, connected_realm_id) -> dict:
        url_name = 'auction'
        ids = {'connected_realm_id':connected_realm_id}
        return await self._fetch_get(url_name, ids)

    async def get_profession_index(self) -> dict:
        url_name = 'profession_index'
        return await self._fetch_get(url_name)

    async def get_profession_tiers(self, profession_id) -> dict:
        url_name = 'profession_skill_tier'
        ids = {'profession_id':profession_id}
        return await self._fetch_get(url_name, ids)

    async def get_profession_icon(self, profession_id) -> bytes:
        url_name = 'profession_icon'
        ids = {'profession_id':profession_id}
        return await self._fetch_get(url_name, ids)

    async def get_profession_tier_categories(
        self, profession_id, skill_tier_id
    ) -> dict:
        url_name = 'profession_tier_detail'
        ids = {'profession_id':profession_id, 'skill_tier_id':skill_tier_id}
        return await self._fetch_get(url_name, ids)

    async def get_recipe(self, recipe_id) -> dict:
        url_name = 'recipe_detail'
        ids = {'recipe_id':recipe_id}
        return await self._fetch_get(url_name, ids)

    async def get_recipe_icon(self, recipe_id) -> bytes:
        url_name = 'repice_icon'
        ids = {'recipe_id':recipe_id}
        return await self._fetch_get(url_name, ids)

    async def get_item_classes(self) -> dict:
        url_name = 'item_classes'
        return await self._fetch_get(url_name)

    async def get_item_subclasses(self, item_class_id) -> dict:
        url_name = 'item_subclass'
        ids = {'item_class_id':item_class_id}
        return await self._fetch_get(url_name, ids)

    async def get_item_set_index(self) -> dict:
        url_name = 'item_set_index'
        return await self._fetch_get(url_name)

    async def get_item_icon(self, item_id) -> bytes:
        url_name = 'item_icon'
        ids = {'item_id':item_id}
        return await self._fetch_get(url_name, ids)

    async def get_wow_token(self) -> dict:
        url_name = 'wow_token'
        return await self._fetch_get(url_name)

    async def get_connected_realm_index(self) -> dict:
        pass

    async def close(self):
        await self.session.close()

async def main():
    for i in range(10):
        us = await WowApi.create('us')
        start = time.time()
        await us.item_search(**{'id':'(0,)'})
        end = time.time()
        print(end - start)
        await us.close()

if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())


