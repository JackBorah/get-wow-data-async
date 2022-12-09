import unittest
import asyncio
import aiohttp
from pprint import pprint

from getwowdataasync import WowApi
from getwowdataasync.urls import *
from urllib.parse import urljoin

class TestFasterMethods(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.TestApi = await WowApi.create("us")

    async def asyncTearDown(self):
        await asyncio.sleep(0) # prevents an annoying warning
        await self.TestApi.close()
        await asyncio.sleep(1/10) # prevents an annoying warning

    async def test_search_data_with_realms(self):
        ordering = {"orderby": "id"}
        actual_response = await self.TestApi._search_data('search_realm', ordering)

        actual_id = actual_response['results'][0]['data']['id']
        expected_id = 4

        self.assertEqual(expected_id, actual_id)

    async def test_search_data_with_items(self):
        ordering = {"id": "[0,]", "orderby": "id", "_pageSize": 1}
        actual_response = await self.TestApi._search_data('search_item', ordering)

        actual_id = actual_response['results'][0]['data']['id']
        expected_id = 25

        self.assertEqual(expected_id, actual_id)

    async def test_make_search_request(self):
        url = urljoin(base_url, paths['search_item'])
        url = url.format(region='us')
        try:
            json = await self.TestApi._make_search_request(url)
        except aiohttp.ClientResponseError as e:
            # this func just makes a get request
            # it succeeding means making a good
            # request who cares if it is a 401
            self.assertEqual(e.status, 401)

    async def test_connected_realm_search(self):
        ordering = {"id": "[0,]", "orderby": "id", "_pageSize": 1}
        actual_response = await self.TestApi.connected_realm_search(ordering)

        actual_id = actual_response['results'][0]['data']['id']
        expected_id = 4

        self.assertEqual(expected_id, actual_id)


    async def test_item_search(self):
        filters = {"id": "[0,]", "orderby": "id", "_pageSize": 1}
        actual_response = await self.TestApi.item_search(filters)

        actual_id = actual_response['results'][0]['data']['id']
        expected_id = 25

        self.assertEqual(expected_id, actual_id)
        

    async def test_get_connected_realms_by_id(self):
        actual_response = await self.TestApi.get_connected_realms_by_id(4)

        actual_id = actual_response['id']
        expected_id = 4

        self.assertEqual(expected_id, actual_id)

    async def test_get_auctions(self):
        actual_response = await self.TestApi.get_auctions(4)

        self.assertTrue(actual_response['auctions']) 

    async def test_get_commodities(self):
        actual_response = await self.TestApi.get_commodities()

        self.assertTrue(actual_response['auctions'])

    async def test_get_profession_index(self):
        actual_response = await self.TestApi.get_profession_index()

        actual_first_profession_id = actual_response['professions'][0]['id']
        expected_first_profession_id = 202

        self.assertEqual(expected_first_profession_id, actual_first_profession_id)

    async def test_get_profession_tiers(self):
        actual_response = await self.TestApi.get_profession_tiers(164)

        actual_id = actual_response['id']
        expected_id = 164

        self.assertEqual(expected_id, actual_id)

    async def test_get_profession_icon(self):
        actual_response = await self.TestApi.get_profession_icon(164)

        self.assertTrue(actual_response)

    async def test_get_recipe_categories(self):
        actual_response = await self.TestApi.get_recipe_categories(164, 2477)

        actual_first_category_name = actual_response['categories'][0]['name']
        expected_first_category_name = 'Weapon Mods'

        self.assertEqual(expected_first_category_name, actual_first_category_name) # TODO change to check if last item is the expectd item

    async def test_get_recipe(self):
        actual_response = await self.TestApi.get_recipe(1631)

        actual_item_id = actual_response['crafted_item']['id']
        expected_item_id = 2862

        self.assertEqual(expected_item_id, actual_item_id) # TODO change to check if last item is the expectd item

    async def test_get_recipe_icon(self):
        actual_response = await self.TestApi.get_recipe_icon(1631)

        self.assertTrue(actual_response) # TODO change to check if last item is the expectd item

    async def test_get_item_classes(self):
        actual_response = await self.TestApi.get_item_classes()

        actual_first_item_class_id = actual_response['item_classes'][0]['id']
        expected_first_item_class_id = 17

        self.assertEqual(expected_first_item_class_id, actual_first_item_class_id)

    async def test_get_item_subclasses(self):
        actual_response = await self.TestApi.get_item_subclasses(0)

        actual_subclass_id = actual_response['class_id']
        expected_subclass_id = 0

        self.assertEqual(expected_subclass_id, actual_subclass_id) # TODO change to check if last item is the expectd item

    async def test_get_item_set_index(self):
        actual_response = await self.TestApi.get_item_set_index()

        self.assertTrue(actual_response['item_sets']) # TODO change to check if last item is the expectd item

    async def test_get_item_icon(self):
        actual_response = await self.TestApi.get_item_icon(19019)

        self.assertTrue(actual_response) # TODO change to check if last item is the expectd item

    async def test_get_wow_token(self):
        actual_response = await self.TestApi.get_wow_token()

        self.assertTrue(actual_response['price']) # TODO change to check if last item is the expectd item

    async def test_get_connected_realm_index(self):
        actual_response = await self.TestApi.get_connected_realm_index()

        self.assertTrue(actual_response['connected_realms']) # TODO change to check if last item is the expectd item

if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    unittest.main()