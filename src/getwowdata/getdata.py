import asyncio
import os
import time
from pprint import pprint

import aiohttp
from dotenv import load_dotenv

from getwowdata.urls import urls
from getwowdata.helpers import *

class WowApi():
    
    @classmethod
    async def create(cls, region):
        self = WowApi() 
        self.region = region 
        self.session = aiohttp.ClientSession(raise_for_status=True)   
        await self.get_access_token()   
        return self 

    async def get_access_token(self, wow_api_id = None, wow_api_secret = None) -> None:
        load_dotenv()
        id = os.environ["wow_api_id"]
        secret = os.environ["wow_api_secret"]
        token_data = {"grant_type": "client_credentials"}
        wow_api_id = wow_api_id
        wow_api_secret = wow_api_secret

        async with self.session.post(urls['access_token'].format(region=self.region), auth=aiohttp.BasicAuth(id, secret), data=token_data) as response:
            response = await response.json()
            self.access_token = response['access_token']
    
    async def connected_realm_search(self, timeout = 60, **extra_params: dict) -> dict:

        if extra_params.get('timeout'):
            timeout = extra_params.pop('timeout')

        search_params = {
            **{
                "access_token": self.access_token,
                "namespace": f"dynamic-{self.region}",
            },
            **extra_params,
        }
        async with self.session.get(urls["search_realm"].format(region=self.region), params=search_params, timeout = timeout) as response:
            json = await response.json()
            json['Date'] = response.headers['Date']
            return await json

    async def _get_item(self, url: str, timeout: int, params: dict) -> dict:
        async with self.session.get(url, timeout=timeout, params=params) as item_data:
            return await item_data.json(content_type=None)

    @retry(10)
    async def item_search(self, **extra_params: dict) -> dict:
        if extra_params.get('timeout'):
            timeout = extra_params.pop('timeout')
        else:
            timeout = 300

        params = {
                "access_token": self.access_token,
                "namespace": f"static-{self.region}",
            }

        search_params = {
            **params,
            **extra_params,
        }
        async with self.session.get(urls["search_item"].format(region=self.region), params=search_params, timeout = timeout) as response:
            json = await response.json()
            tasks = []
            if json.get('results'):
                for item in json['results']:
                    task = asyncio.create_task(self._get_item(item['key']['href'], timeout, params=params))
                    tasks.append(task)
            items = await asyncio.gather(*tasks)
            json = {}
            json['items'] = items
            json['Date'] = response.headers['Date']
            return json


    async def get_connected_realms_by_id(
        self, connected_realm_id: int, timeout: int = 30
    ) -> dict:
        search_params = {
            **{
                "access_token": self.access_token,
                "namespace": f"dynamic-{self.region}",
            },

        }
        async with self.session.get(urls["search_item"].format(region=self.region), params=search_params, timeout = timeout) as response:
            
            json = await response.json()
            json['Date'] = response.headers['Date']
            return await json

    async def get_auctions(self, connected_realm_id, timeout=30) -> dict:
        if extra_params.get('timeout'):
            timeout = extra_params.pop('timeout')

        search_params = {
            **{
                "access_token": self.access_token,
                "namespace": f"dynamic-{self.region}",
            },
            **extra_params,
        }
        async with self.session.get(urls["search_item"].format(region=self.region), params=search_params, timeout = timeout) as response:
            
            json = await response.json()
            json['Date'] = response.headers['Date']
            return await json

    async def get_profession_index(self, timeout=30) -> dict:
        if extra_params.get('timeout'):
            timeout = extra_params.pop('timeout')

        search_params = {
            **{
                "access_token": self.access_token,
                "namespace": f"dynamic-{self.region}",
            },
            **extra_params,
        }
        async with self.session.get(urls["search_item"].format(region=self.region), params=search_params, timeout = timeout) as response:
            
            json = await response.json()
            json['Date'] = response.headers['Date']
            return await json

    async def get_profession_tiers(self, profession_id, timeout=30) -> dict:
        if extra_params.get('timeout'):
            timeout = extra_params.pop('timeout')

        search_params = {
            **{
                "access_token": self.access_token,
                "namespace": f"dynamic-{self.region}",
            },
            **extra_params,
        }
        async with self.session.get(urls["search_item"].format(region=self.region), params=search_params, timeout = timeout) as response:
            
            json = await response.json()
            json['Date'] = response.headers['Date']
            return await json

    async def get_profession_icon(self, profession_id, timeout=30) -> bytes:
        if extra_params.get('timeout'):
            timeout = extra_params.pop('timeout')

        search_params = {
            **{
                "access_token": self.access_token,
                "namespace": f"dynamic-{self.region}",
            },
            **extra_params,
        }
        async with self.session.get(urls["search_item"].format(region=self.region), params=search_params, timeout = timeout) as response:
            
            json = await response.json()
            json['Date'] = response.headers['Date']
            return await json

    async def get_profession_tier_categories(
        self, profession_id, skill_tier_id, timeout=30
    ) -> dict:
        if extra_params.get('timeout'):
            timeout = extra_params.pop('timeout')

        search_params = {
            **{
                "access_token": self.access_token,
                "namespace": f"dynamic-{self.region}",
            },
            **extra_params,
        }
        async with self.session.get(urls["search_item"].format(region=self.region), params=search_params, timeout = timeout) as response:
            
            json = await response.json()
            json['Date'] = response.headers['Date']
            return await json

    async def get_recipe(self, recipe_id, timeout=30) -> dict:
        if extra_params.get('timeout'):
            timeout = extra_params.pop('timeout')

        search_params = {
            **{
                "access_token": self.access_token,
                "namespace": f"dynamic-{self.region}",
            },
            **extra_params,
        }
        async with self.session.get(urls["search_item"].format(region=self.region), params=search_params, timeout = timeout) as response:
            
            json = await response.json()
            json['Date'] = response.headers['Date']
            return await json

    async def get_recipe_icon(self, recipe_id, timeout=30) -> bytes:
        if extra_params.get('timeout'):
            timeout = extra_params.pop('timeout')

        search_params = {
            **{
                "access_token": self.access_token,
                "namespace": f"dynamic-{self.region}",
            },
            **extra_params,
        }
        async with self.session.get(urls["search_item"].format(region=self.region), params=search_params, timeout = timeout) as response:
            
            json = await response.json()
            json['Date'] = response.headers['Date']
            return await json

    async def get_item_classes(self, timeout=30) -> dict:
        if extra_params.get('timeout'):
            timeout = extra_params.pop('timeout')

        search_params = {
            **{
                "access_token": self.access_token,
                "namespace": f"dynamic-{self.region}",
            },
            **extra_params,
        }
        async with self.session.get(urls["search_item"].format(region=self.region), params=search_params, timeout = timeout) as response:
            
            json = await response.json()
            json['Date'] = response.headers['Date']
            return await json

    async def get_item_subclasses(self, item_class_id, timeout=30) -> dict:
        if extra_params.get('timeout'):
            timeout = extra_params.pop('timeout')

        search_params = {
            **{
                "access_token": self.access_token,
                "namespace": f"dynamic-{self.region}",
            },
            **extra_params,
        }
        async with self.session.get(urls["search_item"].format(region=self.region), params=search_params, timeout = timeout) as response:
            
            json = await response.json()
            json['Date'] = response.headers['Date']
            return await json

    async def get_item_set_index(self, timeout=30) -> dict:
        if extra_params.get('timeout'):
            timeout = extra_params.pop('timeout')

        search_params = {
            **{
                "access_token": self.access_token,
                "namespace": f"dynamic-{self.region}",
            },
            **extra_params,
        }
        async with self.session.get(urls["search_item"].format(region=self.region), params=search_params, timeout = timeout) as response:
            
            json = await response.json()
            json['Date'] = response.headers['Date']
            return await json

    async def get_item_icon(self, item_id, timeout=30) -> bytes:
        if extra_params.get('timeout'):
            timeout = extra_params.pop('timeout')

        search_params = {
            **{
                "access_token": self.access_token,
                "namespace": f"dynamic-{self.region}",
            },
            **extra_params,
        }
        async with self.session.get(urls["search_item"].format(region=self.region), params=search_params, timeout = timeout) as response:
            
            json = await response.json()
            json['Date'] = response.headers['Date']
            return await json

    async def get_wow_token(self, timeout=30) -> dict:
        if extra_params.get('timeout'):
            timeout = extra_params.pop('timeout')

        search_params = {
            **{
                "access_token": self.access_token,
                "namespace": f"dynamic-{self.region}",
            },
            **extra_params,
        }
        async with self.session.get(urls["search_item"].format(region=self.region), params=search_params, timeout = timeout) as response:
            
            json = await response.json()
            json['Date'] = response.headers['Date']
            return await json

    async def get_connected_realm_index(self, timeout=30) -> dict:
        if extra_params.get('timeout'):
            timeout = extra_params.pop('timeout')

        search_params = {
            **{
                "access_token": self.access_token,
                "namespace": f"dynamic-{self.region}",
            },
            **extra_params,
        }
        async with self.session.get(urls["search_item"].format(region=self.region), params=search_params, timeout = timeout) as response:
            
            json = await response.json()
            json['Date'] = response.headers['Date']
            return await json

    async def close(self):
        await self.session.close()

async def main():
    for i in range(5):
        us = await WowApi.create('us')
        start = time.time()
        await us.item_search(**{'id':'(0,)'})
        end = time.time()
        print(end - start)
        await us.close()

if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())


