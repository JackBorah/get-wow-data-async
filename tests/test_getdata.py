import asyncio
import unittest
from unittest.mock import AsyncMock, Mock, patch
from urllib.parse import urljoin

import aiohttp
from getwowdataasync.urls import *
from getwowdataasync.getdata import WowApi
from getwowdataasync.helpers import *
from dotenv import load_dotenv


# TODO Still uses aiohttp and is BOKEN because of it. Integreated tests work though.

def create_mock_get_response(self, mock_get, dummy_response):
    mock_get.return_value.__aenter__.return_value.json = AsyncMock(return_value=dummy_response)

class TestGetAccessToken(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.patcher = patch('aiohttp.ClientSession.post')
        cls.mock_post = cls.patcher.start()
        cls.create_mock_access_token_post_response(cls)

    def create_mock_access_token_post_response(self):
        dummy_access_token = {'access_token':'DummyAccessToken'}
        self.mock_post.return_value.__aenter__.return_value.json = AsyncMock(return_value=dummy_access_token)

    @classmethod
    def tearDownClass(cls):
        cls.patcher.stop()

    async def asyncSetUp(self):
        self.TestApi = await WowApi.create('us')

    async def asyncTearDown(self):
        await self.TestApi.close()

    def test_url_joined_correctly(self):
        actual_url = urljoin(base_url, paths['connected_realm_index'])
        expected_url = "https://{region}.api.blizzard.com/data/wow/connected-realm/index"

        self.assertEqual(expected_url, actual_url)

    async def test_get_access_token_returns_expected_token(self):

        actual_access_token = self.TestApi.access_token
        expected_access_token = 'DummyAccessToken'

        self.assertEqual(expected_access_token, actual_access_token)

class TestGetDataIsSuccessful(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        WowApi._get_access_token = AsyncMock(return_value='DummyAccessToken')
        self.TestApi = await WowApi.create("us")

    async def asyncTearDown(self) -> None:
        await self.TestApi.close()

    async def test_WowApi_has_expected_access_token(self):
        actual_access_token = self.TestApi.access_token
        expected_access_token = 'DummyAccessToken'

        self.assertEqual(expected_access_token, actual_access_token)

    async def test_WowApi_has_expected_region(self):
        actual_region = self.TestApi.region
        expected_region = 'us'

        self.assertEqual(expected_region, actual_region)

    async def test_WowApi_has_expected_locale(self):
        actual_locale = self.TestApi.locale
        expected_locale = 'en_US'

        self.assertEqual(expected_locale, actual_locale)

    def test_make_required_auth_and_query_params_correctly_matches_to_dynamic(self):
        params = self.TestApi._make_required_auth_and_query_params("connected_realm_index")
        actual_namespace = params['namespace']
        expected_namespace = 'dynamic-us'

        self.assertEqual(expected_namespace, actual_namespace)

    def test_make_required_auth_and_query_params_correctly_matches_to_static(self):
        params = self.TestApi._make_required_auth_and_query_params("repice_icon")
        actual_namespace = params['namespace']
        expected_namespace = 'static-us'

        self.assertEqual(expected_namespace, actual_namespace)

    def test_make_required_auth_and_query_params_correctly_matches_to_static(self):
        params = self.TestApi._make_required_auth_and_query_params("search_realm")
        actual_namespace = params['namespace']
        expected_namespace = 'dynamic-us'

        self.assertEqual(expected_namespace, actual_namespace)

    def test_make_required_auth_and_query_params_correctly_matches_to_static(self):
        params = self.TestApi._make_required_auth_and_query_params("search_item")
        actual_namespace = params['namespace']
        expected_namespace = 'static-us'

        self.assertEqual(expected_namespace, actual_namespace)


    @patch('aiohttp.ClientSession.get')
    async def test_make_get_request_when_url_has_namespace(self, mock_get):
        dummy_url = 'www.dummy.com/?namespace=test'
        dummy_response = {'test': 'response'}
        create_mock_get_response(self, mock_get, dummy_response)

        actual_respnose = await self.TestApi._make_get_request(dummy_url)

        self.assertEqual(dummy_response, actual_respnose)

    @patch('aiohttp.ClientSession.get')
    async def test_make_get_request_when_url_has_no_namespace(self, mock_get):
        dummy_url = 'www.{region}.dummy.com/'
        dummy_response = {'test': 'response'}
        create_mock_get_response(self, mock_get, dummy_response)

        actual_response = await self.TestApi._make_get_request(dummy_url)
        
        self.assertEqual(dummy_response, actual_response)

    @patch('aiohttp.ClientSession.get')
    async def test_get_data_works_with_url_name(self, mock_get):
        dummy_response = {"key": 1}
        create_mock_get_response(self, mock_get, dummy_response)

        resp = await self.TestApi._get_data("connected_realm_index")

        actual_response = resp['key']
        expected_response = dummy_response['key']

        self.assertEqual(expected_response, actual_response)

    @patch('aiohttp.ClientSession.get')
    async def test_get_data_works_with_already_formatted_url(self, mock_get):
        dummy_response = {"key": 1}
        create_mock_get_response(self, mock_get, dummy_response)

        resp = await self.TestApi._get_data("www.dummy.com/?access_token=123")

        actual_response = resp['key']
        expected_response = dummy_response['key']

        self.assertEqual(expected_response, actual_response)

    def test_build_urls_with_url_name(self):
        dummy_base_url = "https://dummy.com"
        dummy_path = "connected_realm_index"

        actual_url = self.TestApi._build_urls(dummy_base_url, dummy_path)
        expected_url = "https://dummy.com/data/wow/connected-realm/index"

        self.assertEqual(expected_url, actual_url)

    def test_format_url_with_unformatted_url(self):
        dummy_url = "https://{region}.api.blizzard.com/data/wow/connected-realm/index"

        actual_url = self.TestApi._format_url(dummy_url)
        expected_url = "https://us.api.blizzard.com/data/wow/connected-realm/index"

        self.assertEqual(expected_url, actual_url)

    def test_format_url_with_url_name_item_search(self):
        dummy_url = "https://{region}.api.blizzard.com/data/wow/item/{item_id}"
        dummy_path_ids = {"item_id" : 1}

        actual_url = self.TestApi._format_url(dummy_url, dummy_path_ids)
        expected_url = "https://us.api.blizzard.com/data/wow/item/1"

        self.assertEqual(expected_url, actual_url)


    @patch('aiohttp.ClientSession.get')
    async def test_search_data_with_realms(self, mock_get):        
        dummy_response = {"key": 1}
        create_mock_get_response(self, mock_get, dummy_response)

        response = await self.TestApi._search_data("search_realm")

        self.assertEqual(response["key"], dummy_response["key"])

    @patch('aiohttp.ClientSession.get')
    async def test_search_data_with_items(self, mock_get):
        dummy_response = {"results": [{"key": {"href": "https://dummyurl.com/"}}]}
        create_mock_get_response(self, mock_get, dummy_response)

        response = await self.TestApi._search_data("search_item", {"id": "1"})
        expected_resp = {"results": [{"key": {"href": "https://dummyurl.com/"}}]}

        self.assertEqual(response, expected_resp)

    @patch('aiohttp.ClientSession.get')
    async def test_make_search_request(self, mock_get):
        dummy_url = "https://dummyurl.com/"
        dummy_response = 'success'

        create_mock_get_response(self, mock_get, dummy_response)
        actual_response = await self.TestApi._make_get_request(dummy_url)

        self.assertEqual(dummy_response, actual_response)

    @patch('getwowdataasync.WowApi._search_data')
    @patch('getwowdataasync.WowApi._get_data')
    async def test_get_all_items(self, mocked_get_data, mocked_search_data):
        # looping through item search starting from id = 0
        # making a request to each item's href and appending
        # that json to a list.
        # ending when a search returns nothing? (whatever happens when the last id is reached)
        
        dummy_search_data_response = [
            {
                'results' : [   
                    {
                        'key': {
                            'href' : "https://dummyurl.com/"
                            },
                        'data': {
                            'id' : 1
                            }
                    }
                ]
            },
            {
                'results': []
            }
        ]

        dummy_item_response = {'id':1}

        mocked_search_data.side_effect = dummy_search_data_response
        mocked_get_data.return_value = dummy_item_response

        actual_response = await self.TestApi.get_all_items()
        expected_response = [dummy_item_response]

        self.assertEqual(expected_response, actual_response)

    async def test_get_detailed_list_of_elements(self):
        pass

    @patch('getwowdataasync.WowApi.get_connected_realm_index')
    @patch('getwowdataasync.WowApi._get_data')
    async def test_get_all_realms(self, mocked_get_data, mocked_get_connected_realm_index):
        # looping through item search starting from id = 0
        # making a request to each item's href and appending
        # that json to a list.
        # ending when a search returns nothing? (whatever happens when the last id is reached)
        
        dummy_connected_realms_index_response = {
                'connected_realms' : [   
                    {
                        'href': "https://dummyurl.com/" 
                    }
                ]
            }

        dummy_item_response = {'data': {'id':1}}

        mocked_get_connected_realm_index.return_value = dummy_connected_realms_index_response
        mocked_get_data.return_value = dummy_item_response

        actual_response = await self.TestApi.get_all_realms()
        expected_response = [dummy_item_response]

        self.assertEqual(expected_response, actual_response)

    @patch('getwowdataasync.WowApi._search_data')
    @patch('getwowdataasync.WowApi._get_detailed_list_of_elements')
    async def test_get_items_by_expansion(self, _get_detailed_list_of_elements, mocked_search_data):
        dummy_search_data_response = [
            {
                'results' : [   
                    {
                        'key': {
                            'href' : "https://dummyurl.com/"
                            },
                        'data': {
                            'id' : 1
                            }
                    }
                ]
            },
            {
                'results': []
            }
        ]
        dummy_get_detailed_list_of_elements = [{'data': {'id':1}}]

        mocked_search_data.side_effect = dummy_search_data_response
        _get_detailed_list_of_elements.return_value = dummy_get_detailed_list_of_elements

        actual_response = await self.TestApi.get_items_by_expansion('df')
        expected_response = dummy_get_detailed_list_of_elements

        self.assertEqual(expected_response, actual_response)

    @patch('getwowdataasync.WowApi.get_profession_index')
    @patch('getwowdataasync.WowApi.get_profession_tiers')
    @patch('getwowdataasync.WowApi.get_recipe_categories')
    @patch('getwowdataasync.WowApi.get_recipe')
    async def test_get_professions_tree_by_expansion(
        self, mock_get_recpie, mock_get_recipe_categories, 
        mock_get_profession_tiers, mock_get_profession_index
        ):
        mock_get_profession_index.return_value = {
            "professions" : [
                {
                    "name" : "Test Profession 1",
                    "id" : 1
                },
                {
                    "name" : "Test Profession 2",
                    "id" : 2   
                },
                {
                    "name" : "Test Profession 3",
                    "id" : 3 
                }
            ]
        }
        mock_get_profession_tiers.return_value = {
            "skill_tiers" : [
                {
                    "name" : "Test tier 1",
                    "id" : 1
                },
                {
                    "name" : "Test tier 2",
                    "id" : 2
                },
                {
                    "name" : "Dragon Isles Test tier 3",
                    "id" : 3
                },
            ]
        }
        mock_get_recipe_categories.return_value = {
            "categories" : [
                {
                    "name" : "Test Category Name",
                    "recipes" : [
                        {
                            "name" : "Test Recipe Name 1",
                            "id" : 1,
                        },
                        {
                            "name" : "Test Recipe Name 2",
                            "id" : 2,
                        },     
                    ]
                }
            ]
        }
        mock_get_recpie.return_value = {
            "Good" : "Recipe"
        }

        actual_profession_trees = await self.TestApi.get_professions_tree_by_expansion('df')
        expected_profession_trees = [
            {
                "name" : "Test Profession 1",
                "id" : 1,
                "categories" : [
                    {
                        "name" : "Test Category Name",
                        "recipes" : [
                            {
                                "Good" : "Recipe"
                            },
                            {
                                "Good" : "Recipe"
                            }
                        ]
                    }
                ]
            },
            {
                "name" : "Test Profession 2",
                "id" : 2,
                "categories" : [
                    {
                        "name" : "Test Category Name",
                        "recipes" : [
                            {
                                "Good" : "Recipe"
                            },
                            {
                                "Good" : "Recipe"
                            }
                        ]
                    }
                ]       
            },
            {
                "name" : "Test Profession 3",
                "id" : 3,
                "categories" : [
                    {
                        "name" : "Test Category Name",
                        "recipes" : [
                            {
                                "Good" : "Recipe"
                            },
                            {
                                "Good" : "Recipe"
                            }
                        ]
                    }
                ]
            }
        ]

        self.assertListEqual(expected_profession_trees, actual_profession_trees)

    @patch('getwowdataasync.WowApi._get_data')
    async def test_get_profession_index_removes_bad_ids_when_true_professions_only_is_true(self, mock_get_data):
        mock_get_data.return_value = {
            "professions" : [
                {
                    "id" : 794
                },
                {
                    "id" : 999
                },
                {
                    "id" : 1001
                }
            ]
        }
        actual_profession_index = await self.TestApi.get_profession_index()
        expected_profession_index = {
            "professions" : [
                {"id" : 999}
            ]
        }

        self.assertDictEqual(expected_profession_index, actual_profession_index)

    # # TODO blocks and never finishes.
    # # Long and complicated
    # # Might remove anyway
    # async def test_get_all_profession_data(mock_api_instance, mock_aioresponses):
    #     api = mock_api_instance
    #     api.get_profession_index = AsyncMock(return_value=
    #         {
    #         "_links": {
    #             "self": {
    #             "href": "https://us.api.blizzard.com/data/wow/profession/?namespace=static-9.2.7_44981-us"
    #             }
    #         },
    #         "professions": [
    #             {
    #             "key": {
    #                 "href": "https://us.api.blizzard.com/data/wow/profession/202?namespace=static-9.2.7_44981-us"
    #             },
    #             "name": "Engineering",
    #             "id": 202
    #             }
    #         ]
    #     }
    #     )
    #     skill_tier_pattern = re.compile(
    #         "https://us.api.blizzard.com/data/wow/profession/202?namespace=static-9.2.7_44981-us"
    #     )
    #     category_pattern = re.compile(
    #     'https://us.api.blizzard.com/data/wow/profession/202/skill-tier/2499?namespace=static-9.2.7_44981-us' 
    #     )
    #     item_pattern = re.compile(
    #         "https://us.api.blizzard.com/data/wow/recipe/38895?namespace=static-9.2.7_44981-us"
    #     )
    #     skill_tier_data = {
    # "_links": {
    #     "self": {
    #     "href": "https://us.api.blizzard.com/data/wow/profession/202?namespace=static-9.2.7_44981-us"
    #     }
    # },
    # "id": 202,
    # "name": "Engineering",
    # "description": "Higher engineering skill allows you to learn higher level engineering schematics.  Schematics can be found on trainers around the world as well as from quests and monsters.",
    # "type": {
    #     "type": "PRIMARY",
    #     "name": "Primary"
    # },
    # "media": {
    #     "key": {
    #     "href": "https://us.api.blizzard.com/data/wow/media/profession/202?namespace=static-9.2.7_44981-us"
    #     },
    #     "id": 202
    # },
    # "skill_tiers": [
    #     {
    #     "key": {
    #         "href": "https://us.api.blizzard.com/data/wow/profession/202/skill-tier/2499?namespace=static-9.2.7_44981-us"
    #     },
    #     "name": "Kul Tiran Engineering / Zandalari Engineering",
    #     "id": 2499
    #     }]}
    #     categories_data = {
    #         "_links": {
    #             "self": {
    #             "href": "https://us.api.blizzard.com/data/wow/profession/202/skill-tier/2499?namespace=static-9.2.7_44981-us"
    #             }
    #         },
    #         "id": 2499,
    #         "name": "Kul Tiran Engineering / Zandalari Engineering",
    #         "minimum_skill_level": 1,
    #         "maximum_skill_level": 175,
    #         "categories": [
    #             {
    #             "name": "Bombs",
    #             "recipes": [
    #                 {
    #                 "key": {
    #                     "href": "https://us.api.blizzard.com/data/wow/recipe/38895?namespace=static-9.2.7_44981-us"
    #                 },
    #                 "name": "F.R.I.E.D.",
    #                 "id": 38895
    #                 }]}]}
    #     item_data = {
    # "_links": {
    #     "self": {
    #     "href": "https://us.api.blizzard.com/data/wow/recipe/38895?namespace=static-9.2.7_44981-us"
    #     }
    # },
    # "id": 38895,
    # "name": "F.R.I.E.D.",
    # "description": "Craft a F.R.I.E.D.",
    # "media": {
    #     "key": {
    #     "href": "https://us.api.blizzard.com/data/wow/media/recipe/38895?namespace=static-9.2.7_44981-us"
    #     },
    #     "id": 38895
    # },
    # "crafted_item": {
    #     "key": {
    #     "href": "https://us.api.blizzard.com/data/wow/item/153490?namespace=static-9.2.7_44981-us"
    #     },
    #     "name": "F.R.I.E.D.",
    #     "id": 153490
    # },
    # "reagents": [
    #     {
    #     "reagent": {
    #         "key": {
    #         "href": "https://us.api.blizzard.com/data/wow/item/152512?namespace=static-9.2.7_44981-us"
    #         },
    #         "name": "Monelite Ore",
    #         "id": 152512
    #     },
    #     "quantity": 6
    #     },
    #     {
    #     "reagent": {
    #         "key": {
    #         "href": "https://us.api.blizzard.com/data/wow/item/160502?namespace=static-9.2.7_44981-us"
    #         },
    #         "name": "Chemical Blasting Cap",
    #         "id": 160502
    #     },
    #     "quantity": 5
    #     },
    #     {
    #     "reagent": {
    #         "key": {
    #         "href": "https://us.api.blizzard.com/data/wow/item/163569?namespace=static-9.2.7_44981-us"
    #         },
    #         "name": "Insulated Wiring",
    #         "id": 163569
    #     },
    #     "quantity": 8
    #     }
    # ],
    # "rank": 1,
    # "crafted_quantity": {
    #     "value": 1
    # }
    # }
        
    #     mock_aioresponses.get(
    #         skill_tier_pattern,
    #         status=200,
    #         payload=skill_tier_data,
    #     )
    #     mock_aioresponses.get(
    #         category_pattern,
    #         status=200,
    #         payload=categories_data,
    #     )
    #     mock_aioresponses.get(
    #         item_pattern,
    #         status=200,
    #         payload=item_data,
    #     )

    #     actual_result = await api.get_all_profession_data()
    #     expected_result = [
    #         {
    #             'name': 'Engineering',
    #             'id': 202,
    #             'skill_tiers': [
    #                 {
    #                     'name': 'Kul Tiran Engineering / Zandalari Engineering',
    #                     'id': 2499,
    #                     'categories' : [
    #                         {
    #                             'name': 'Bombs',
    #                             'recipes': [
    #                                     item_data
    #                             ]
    #                         }
    #                     ]
    #                 }
    #             ]
    #         }
    #     ]
    #     assert expected_result == actual_result
    
if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    unittest.main()
