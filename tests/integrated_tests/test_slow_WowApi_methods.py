#Don't run TestSlowMethods unless your have a day to spare

import unittest
import asyncio
from pprint import pprint

from getwowdataasync import WowApi
from getwowdataasync.urls import *

class TestSlowMethods(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.TestApi = await WowApi.create("us")

    async def asyncTearDown(self):
        await asyncio.sleep(0) # prevents an annoying warning
        await self.TestApi.close()
        await asyncio.sleep(1/10) # prevents an annoying warning

    # Takes too  long for regular testing
    async def test_get_all_items(self):
        all_items = await self.TestApi.get_all_items()

        self.assertGreater(len(all_items), 100000)

    async def test_get_all_realms(self):
        actual_output = await self.TestApi.get_all_realms()
        
        self.assertTrue(actual_output)
        
    async def test_get_items_by_expansion(self):
        actual_response = await self.TestApi.get_items_by_expansion('df')

        pprint(actual_response[-1])

        self.assertTrue(actual_response) # TODO change to check if last item is the expectd item

    async def test_get_profession_index(self):
        actual_response = await self.TestApi.get_profession_index()
        pprint(actual_response)

    async def test_get_professions_tree_by_expansion(self):
        actual_response = await self.TestApi.get_professions_tree_by_expansion('df')

        pprint(actual_response[-1])

        self.assertTrue(actual_response) # TODO change to check if last item is the expectd item

if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    unittest.main()