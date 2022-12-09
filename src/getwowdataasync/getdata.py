## TODO 11/15/2022
## Refactoring to be clean
# Change class, method names to be clearer
    # Change name WowApi to WowApiClient
    # Change get functions name to consume or query?
# Create timeout class which would be passed into WowApiClient, setting timeout params ???
# Reorganize so caller is above callee
# Remove unused code
# make it useable with the 'with' keyword 
    # I think this was so WowApi.close() wouldn't need to be called
# see if one of the retry functions is useless
# remove unused code
# decompose functions into smaller better named ones
# shrink bloated docstrings?
# make a data structure that attaches parsed json and useful response metadata
    # like .ok and return this instead of vanilla dicts from get_x()
    # then tests could access .ok or .url to see why it passed or failed

### Whats the purpose of this package?
### Abstract away making requests to World of Warcrafts Api's.
### Therefore anything at the level of API requests would belong here.

import asyncio
import os
import time
import functools
from pprint import pprint
from urllib.parse import urljoin

import aiohttp
from dotenv import load_dotenv

from getwowdataasync.urls import *
from getwowdataasync.helpers import *

class WowApi:
    """Instantiate with WowApi.create('region'). You need to have
    your blizzard api client credentials inside a .env or passed in.
    Then use its methods to query the API.
    """

    # couldn't get __init__ to work with async
    @classmethod
    async def create(cls, region: str, locale: str = "en_US", wow_api_id: str = None, wow_api_secret: str = None):
        """Gets an instance of WowApi with an access token, region, and aiohttp session.

        Args:
            region (str): Each region has its own data. This specifies which regions data
                WoWApi will consume.
            locale (str): The language some elements will return. 
                Realms, for example, can return their names in a single
                language or all supported ones.
            wow_api_id (str): Your api client id from blizzards api website
            wow_api_secret (str): Your api client secret from blizzards api website
        Returns:
            An instance of the WowApi class.
        """
        self = WowApi()
        self.region = region
        self.locale = locale
        self.timeout = aiohttp.ClientTimeout(connect=5, sock_read=360, sock_connect=5)
        self.session = aiohttp.ClientSession(raise_for_status=True, timeout=self.timeout)
        self.access_token = await self._get_access_token(wow_api_id=wow_api_id, wow_api_secret=wow_api_secret)
        return self

    @retry
    async def _get_access_token(
        self, wow_api_id: str = None, wow_api_secret: str = None
    ) -> None:
        load_dotenv()
        token_data = {"grant_type": "client_credentials"}
        id = wow_api_id or os.environ["wow_api_id"]
        secret = wow_api_secret or os.environ["wow_api_secret"]

        async with self.session.post(
            access_token_url.format(region=self.region),
            auth=aiohttp.BasicAuth(id, secret),
            data=token_data,
        ) as response:
            response = await response.json()
            return response["access_token"]

    # TODO make a url class with format, ... methods
    @retry
    async def _get_data(self, url: str, path_ids: dict = {}) -> dict:
        """Makes requests given formatted or unformatted urls/url_names"""
        params = self._make_required_auth_and_query_params(url)

        if url in paths: # needs to be built
            url = self._build_urls(base_url, url)
        if "{region}" in url: # needs to be formatted
            url = self._format_url(url, path_ids)

        json_response = await self._make_get_request(url, path_ids, params)
        return json_response

    def _build_urls(self, base_url :str, path: str) -> str:
        return urljoin(base_url, paths[path])

    def _format_url(self, url: str, path_ids: dict = {}) -> str:
        return url.format(region=self.region, **path_ids)

    def _make_required_auth_and_query_params(self, url: str):
        params = {
            "access_token": self.access_token,
            "locale": self.locale,
        }
        if url in urls_with_static_namespace:
            params = {
                **params,
                "namespace": f"static-{self.region}",
            }
        else:
            params = {
                **params,
                "namespace": f"dynamic-{self.region}",
            }

        return params

    # takes both formatted and unformatted urls
    # aka with and without region, or other params specified
    async def _make_get_request(self, url: str, path_ids: dict = {}, params: dict = {}):
        formatted_url = self._format_url(url, path_ids)
        
        async with self.session.get(
            formatted_url, params=params
        ) as response:
            json = await response.json()
            return json

    @retry
    async def _search_data(self, url_name: str, search_parameters: dict = {}) -> dict:
        required_params = self._make_required_auth_and_query_params(url_name)

        search_parameters = {
            **required_params,
            **search_parameters
        }

        url = self._build_urls(base_url, url_name)
        url = self._format_url(url)

        json_response = await self._make_search_request(url, search_parameters)
        return json_response

    async def _make_search_request(self, url: str, search_parameters: dict = {}):
        async with self.session.get(
            url, params=search_parameters
        ) as response:
            json = await response.json()
            return json

    async def get_all_items(self) -> list:
        """Adds all urls from an item or realm search to the queue.

        A worker is then needed to remove urls from the queue and make requests with them.
        """
        url_name = 'search_item'
        params_to_start_search_from_id_0 = {"id": "[0,]", "orderby": "id", "_pageSize": 1000}
        items = []
        from pprint import pprint
        print("Starting search...")
        set_of_items = await self._search_data(url_name, params_to_start_search_from_id_0)
        while set_of_items['results']:
            items += await self._get_detailed_list_of_elements(items, set_of_items)
            print('finshed 1000 items! continuing...')
            next_id_in_sequence = items[-1]['id'] + 1  # +1 so that the last item search returns empty
            prams_to_search_next_set_of_ids = {"orderby": "id", "id": f"[{next_id_in_sequence},]", "_pageSize": 1000}
            print(len(items))
            print(items[-1]['id'])
            set_of_items = await self._search_data(url_name, prams_to_search_next_set_of_ids)

        print("Finished getting all items!")
        return items

    # A search returns data on the items but is missing some
    # important details. This Makes a request to each individual
    # item to get all its information
    async def _get_detailed_list_of_elements(self, collection: list, json: str):
        temp_collection = []
        for item in json["results"]:
            await asyncio.sleep(1/10) # need to throttle to prevent 429

            item_id = item["data"]["id"]
            item_response = await self.get_item_by_id(item_id)
            temp_collection.append(item_response)
            print(len(temp_collection))
        return temp_collection

    async def get_item_by_id(self, item_id: int):
        url_name = "item"
        path_ids = {"item_id": item_id}
        return await self._get_data(url_name, path_ids)

    async def get_all_realms(self) -> list:
        """Returns all realms in WowApi's given region."""
        connected_realms_index = await self.get_connected_realm_index()
        realms = []

        for realm in connected_realms_index['connected_realms']:
            print(len(realms))
            realm = await self._get_data(realm['href'])
            realms.append(realm)
        
        return realms

    async def get_items_by_expansion(self, expansion_name: str) -> list:
        """Gets all items from an expansion.

        Currently only Dragonflight is supported.
        To extend find the first and last item id's of
        each expansion.

        Args:
            expansion_name (str): Name of a WoW expansion.
                Ex: "Classic", "Burning Crusade", "Dragonflight"

        Returns:
            A list containing all the items from the 
            specified expansion.
        """
        expansions = {
            'df' : [188658, 1000000000]
        }
        expansions_min_max_ids = expansions[expansion_name]    
        items = []
        start_id = expansions_min_max_ids[0]
        end_id = expansions_min_max_ids[1]
        url_name = 'search_item'
        starting_params = {"orderby": "id", "id": f"[{start_id},]", "_pageSize": 1000}

        set_of_items = await self._search_data(url_name, starting_params)
        while set_of_items['results'] and start_id < end_id:
            items += await self._get_detailed_list_of_elements(items, set_of_items)
            start_id = items[-1]['data']['id'] + 1  # +1 so that the last item search returns empty
            prams_to_search_next_set_of_ids = {"orderby": "id", "id": f"[{start_id},]", "_pageSize": 1000}

            set_of_items = await self._search_data('items', prams_to_search_next_set_of_ids)
        
        return items

    async def get_professions_tree_by_expansion(self, expansion_name: str) -> list:
        """Returns all professions and recipes from a provided expaneion.

        Args:
            Expansion_name (str): The initals of an expansion. Currently only 'df'
                for Dragonflight is currently supported.

        Returns:
            A list of profession dictionaries with all of that
            profession's recipes divided by caregory ('Shields, Armor, ...')
        
        """
        professions = []

        profession_index = await self.get_profession_index()
        for profession in profession_index['professions']:
            profession_id = profession['id']
            profession_name = profession['name']

            print(f"Getting {profession_name}'s recipes")
            profession_tree = {
                'name' : profession_name,
                'id': profession_id,
                'categories': []
            }
            skill_tiers = await self.get_profession_tiers(profession_id)
            for skill_tier in skill_tiers['skill_tiers']:
                if 'Dragon Isles' in skill_tier['name']:
                    recipe_categories = await self.get_recipe_categories(profession['id'], skill_tier['id'])
                    for category in recipe_categories['categories']:
                        category_name = category['name']

                        print(f"Getting {category_name}")
                        category_branch = {
                            'name' : category_name,
                            'recipes': []
                        }
                        for recipe in category['recipes']:
                            recipe_leaf = await self.get_recipe(recipe['id'])
                            category_branch['recipes'].append(recipe_leaf)
        
                        profession_tree['categories'].append(category_branch)
            professions.append(profession_tree)
        return professions

    async def connected_realm_search(self, filters: dict = {}) -> dict:
        """Preforms a search of all realms in that region.

        Args:
            filters (dict): Parameters for refining a search request.
                See https://develop.battle.net/documentation/world-of-warcraft/guides/search

        Returns:
            The search results as json parsed into a dict.
        """
        url_name = "search_realm"
        realm_json = await self._search_data(url_name, filters)
        return realm_json

    async def item_search(self, filters: dict) -> dict:
        """Preforms a search of all items.

        Args:
            extra_params (dict): Parameters for refining a search request.
                See https://develop.battle.net/documentation/world-of-warcraft/guides/search

        Returns:
            The search results as json parsed into a dict.
        """
        url_name = "search_item"
        items_json = await self._search_data(url_name, filters)
        return items_json

    async def get_connected_realms_by_id(self, connected_realm_id: int) -> dict:
        """Returns the all realms in a connected realm by their connected realm id.

        Args:
            connected_realm_id (int):
                The id of a connected realm cluster.
        """
        url_name = "realm"
        ids = {"connected_realm_id": connected_realm_id}
        return await self._get_data(url_name, ids)

    async def get_auctions(self, connected_realm_id) -> dict:
        """Returns the all auctions in a connected realm by their connected realm id.

        Args:
            connected_realm_id (int):
                The id of a connected realm cluster.
        """
        url_name = "auction"
        ids = {"connected_realm_id": connected_realm_id}
        return await self._get_data(url_name, ids)

    async def get_commodities(self) -> dict:
        """Returns all commodities data for the region."""
        url_name = 'commodities'
        return await self._get_data(url_name)


    async def get_profession_index(self, true_professions_only: bool = True) -> dict:
        """Returns the all professions.
        
        Args:
            true_professions_only (bool):
                When true (defualt) this only returns primary and 
                secondary professions like jewelcrafting, 
                leatherworking, ... not strange ones like
                protoform synthesis or archaeology (rip).
        """
        url_name = "profession_index"
        professions_index = await self._get_data(url_name)

        if true_professions_only:
            true_professions = []
            for profession in professions_index['professions']:
                if profession['id'] < 1000 and profession['id'] != 794:
                    true_professions.append(profession)
            professions_index['professions'] = true_professions
        return professions_index

    async def get_profession_tiers(self, profession_id: int) -> dict:
        """Returns the all profession skill tiers in a profession by their profession id.

        A profession teir includes all the recipes from that expansion.
        Teir examples are classic, tbc, shadowlands, ...

        Args:
            profession_id (int):
                The id of a profession. Get from get_profession_index().
        """
        url_name = "profession_skill_tier"
        ids = {"profession_id": profession_id}
        return await self._get_data(url_name, ids)

    async def get_profession_icon(self, profession_id: int) -> dict:
        """Returns json with a link to a professions icon.

        Args:
            profession_id (int): The id of a profession. Get from get_profession_index.
        """
        url_name = "profession_icon"
        ids = {"profession_id": profession_id}
        return await self._get_data(url_name, ids)

    async def get_recipe_categories(
        self, profession_id: int, skill_tier_id: int
    ) -> dict:
        """Returns all crafts from a skill teir.

        Included in this response are the categories like belts, capes, ... and the item within them.
        This is broken down by skill tier (tbc, draenor, shadowlands).

        Args:
            profession_id (int): The profession's id. Found in get_profession_index().
            skill_tier_id (int): The skill teir id. Found in get_profession_teirs().
        """
        url_name = "profession_tier_detail"
        ids = {"profession_id": profession_id, "skill_tier_id": skill_tier_id}
        return await self._get_data(url_name, ids)

    async def get_recipe(self, recipe_id: int) -> dict:
        """Returns a recipe by its id.

        Args:
            recipe_id (int): The id from a recipe. Found in get_profession_tier_details().
        """
        url_name = "recipe_detail"
        ids = {"recipe_id": recipe_id}
        return await self._get_data(url_name, ids)

    async def get_recipe_icon(self, recipe_id: int) -> dict:
        """Returns a dict with a link to a recipes icon.

        Args:
            recipe_id (int): The id from a recipe. Found in get_profession_tier_details().
        """
        url_name = "repice_icon"
        ids = {"recipe_id": recipe_id}
        return await self._get_data(url_name, ids)

    async def get_item_classes(self) -> dict:
        """Returns all item classes (consumable, container, weapon, ...)."""
        url_name = "item_classes"
        return await self._get_data(url_name)

    async def get_item_subclasses(self, item_class_id: int) -> dict:
        """Returns all item subclasses (class: consumable, subclass: potion, elixir, ...).

        Args:
            item_class_id (int): Item class id. Found with get_item_classes().
        """
        url_name = "item_subclass"
        ids = {"item_class_id": item_class_id}
        return await self._get_data(url_name, ids)

    async def get_item_set_index(self) -> dict:
        """Returns all item sets. Ex: teir sets"""
        url_name = "item_set_index"
        return await self._get_data(url_name)

    async def get_item_icon(self, item_id: int) -> dict:
        """Returns a dict with a link to an item's icon.

        Args:
            item_id (int): The items id. Get from item_search().
        """
        url_name = "item_icon"
        ids = {"item_id": item_id}
        return await self._get_data(url_name, ids)

    async def get_wow_token(self) -> dict:
        """Returns data on the regions wow token such as price."""
        url_name = "wow_token"
        return await self._get_data(url_name)

    async def get_connected_realm_index(self) -> dict:
        """Returns a dict of all realm's names with their connected realm id."""
        url_name = "connected_realm_index"
        return await self._get_data(url_name)

    async def close(self):
        """Closes aiohttp.ClientSession."""
        await self.session.close()


     # TODO remove if unused (most likely)
    # async def search_worker(self, url_name: str):
    #     if url_name == "search_item":
    #         item_json = {"items": []}
    #     elif url_name == "search_realm": 
    #         realm_json = {"realms": []}

    #     request_count = 0
    #     while not self.queue.empty():
    #         tasks = []
    #         # start timing 100 task execution
    #         start = time.perf_counter()
    #         while len(tasks) < 100:
    #             if self.queue.empty():
    #                 break
    #             url = self.queue.get_nowait()
    #             task = asyncio.create_task(self._get_item(url))
    #             tasks.append(task)
    #             request_count += 1
    #             await asyncio.sleep(1 / 10)
    #         finished_tasks = await asyncio.gather(*tasks)
    #         for ele in finished_tasks:
    #             if ele == None:
    #                 finished_tasks.remove(None)
    #         end = time.perf_counter()
    #         elapsed = end - start
    #         print(f"100 tasks finished in: {elapsed}")
    #         last_id = finished_tasks[-1]["id"]
    #         print(f"last id: {last_id}")
    #         if url_name == "search_item":
    #             item_json["items"] += finished_tasks
    #         elif url_name == "search_realm":
    #             realm_json["realms"] += finished_tasks

    #         tasks = []

    #     if url_name == "search_item":
    #         return item_json

    #     elif url_name == "search_realm":
    #         return realm_json # a list of connected realm clusters

    # async def get_all_profession_data(self) -> list:
    #     """Returns a nested dictionary of all profession data.

    #     The structure of the returned dict is like:
    #         [
    #             {
    #                 'name' : 'Inscription',
    #                 'id' : x,
    #                 'skill_tiers' : [
    #                     {
    #                         'name' : 'Shadowlands Inscription',
    #                         'id' : y,
    #                         'categories' : [
    #                             {
    #                             'name' : 'some name',
    #                             'recipes' : [
    #                                     {recipe data...},
    #                                     {recipe2 data...},
    #                             ]
    #                             }
    #                         ]

    #                     }
    #                 ]
    #             }
    #         ]
    #     """
    #     profession_tree = []
    #     print("getting profession index...")
    #     profession_index = await self.get_profession_index()
    #     print("got profession index!")
    #     for prof in profession_index["professions"]:
    #         if (
    #             prof["id"] < 1000
    #         ):  # only add actual professions to the tree, not weird ones like protoform synthesis
    #             prof_name = prof["name"]
    #             prof_id = prof["id"]
    #             skill_tier_tree = []
    #             profession_tree.append(
    #                 {"name": prof_name, "id": prof_id, "skill_tiers": skill_tier_tree}
    #             )
    #             print(f"getting {prof_name} skill tier")
    #             skill_tier_index = await self._get_item(prof["key"]["href"])
    #             if skill_tier_index.get("skill_tiers"):
    #                 for skill_tier in skill_tier_index["skill_tiers"]:
    #                     skill_tier_name = skill_tier["name"]
    #                     skill_tier_id = skill_tier["id"]
    #                     categories_tree = []
    #                     skill_tier_tree.append(
    #                         {
    #                             "name": skill_tier_name,
    #                             "id": skill_tier_id,
    #                             "categories": categories_tree,
    #                         }
    #                     )
    #                     print(f"getting {skill_tier_name} category")
    #                     categories_index = await self._get_item(
    #                         skill_tier["key"]["href"]
    #                     )
    #                     if categories_index.get("categories"):
    #                         for category in categories_index["categories"]:
    #                             category_name = category["name"]
    #                             recipe_leaves = []
    #                             categories_tree.append(
    #                                 {"name": category_name, "recipes": recipe_leaves}
    #                             )
    #                             tasks = []
    #                             recipes = []
    #                             start = time.monotonic()
    #                             print(f"getting {category_name} recipes")
    #                             for recipe_obj in category["recipes"]:
    #                                 task = asyncio.create_task(
    #                                     self._get_item(recipe_obj["key"]["href"])
    #                                 )
    #                                 await asyncio.sleep(1 / 10)
    #                                 tasks.append(task)
    #                                 if len(tasks) == 100:
    #                                     end = time.monotonic()
    #                                     elapsed = end - start
    #                                     print(elapsed)
    #                                     recipes = await asyncio.gather(*tasks)
    #                                     recipe_leaves += recipes
    #                                     tasks = []
    #                                     recipes = []
    #                                     start = time.monotonic()
    #                             if len(tasks) != 0:
    #                                 recipes = await asyncio.gather(*tasks)
    #                                 recipe_leaves += recipes

    #     return profession_tree
