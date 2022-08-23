import os
import re
import asyncio
from pprint import pprint
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
import aiohttp
from aioresponses import aioresponses
import getwowdataasync
from getwowdataasync.getdata import WowApi
from dotenv import load_dotenv


@pytest.fixture
def mock_aioresponses():
    with aioresponses() as mocked:
        yield mocked


@pytest_asyncio.fixture
async def mock_api_instance(mock_aioresponses):
    data = {"access_token": "dummytoken"}
    # os.environ["wow_api_id"] = "dummyid"
    # os.environ["wow_api_secret"] = "dummysecret"
    mock_aioresponses.post(
        getwowdataasync.urls["access_token"].format(region="us"),
        status=200,
        payload=data,
    )
    return await getwowdataasync.WowApi.create("us")


@pytest_asyncio.fixture
async def real_api_instance():
    return await getwowdataasync.WowApi.create("us")


async def test_get_access_token(mock_api_instance):
    api = mock_api_instance
    await api.close()
    assert api.access_token == "dummytoken"


async def test_fetch_get_returns_json(mock_aioresponses, mock_api_instance):
    api = mock_api_instance
    pattern = re.compile(
        getwowdataasync.urls["connected_realm_index"].format(region=api.region)
    )
    data = {"key": 1}
    mock_aioresponses.get(
        pattern,
        status=200,
        payload=data,
    )
    resp = await api._fetch_get("connected_realm_index")
    await api.close()
    assert resp["key"] == data["key"]


async def test_fetch_search_with_realms(mock_aioresponses, mock_api_instance):
    api = mock_api_instance
    pattern = re.compile(getwowdataasync.urls["search_realm"].format(region=api.region))
    data = {"key": 1}
    mock_aioresponses.get(
        pattern,
        status=200,
        payload=data,
    )
    resp = await api._fetch_get("search_realm")
    await api.close()
    assert resp["key"] == data["key"]


async def test_fetch_search_with_items(mock_aioresponses, mock_api_instance):
    api = mock_api_instance
    search_pattern = re.compile(
        getwowdataasync.urls["search_item"].format(region=api.region)
    )
    pattern_dummyurl = re.compile("https://dummyurl.com/")
    search_data = {"results": [{"key": {"href": "https://dummyurl.com/"}}]}
    item_data = {"item": 1, "dummyvalue": 2}
    mock_aioresponses.get(
        search_pattern,
        status=200,
        payload=search_data,
    )
    mock_aioresponses.get(
        pattern_dummyurl,
        status=200,
        payload=item_data,
    )

    resp = await api._fetch_search("search_item", {"id": "1"})
    await api.close()
    expected_resp = {"results": [{"key": {"href": "https://dummyurl.com/"}}]}
    assert resp == expected_resp


async def test_search_enqueue_all(mock_api_instance):
    api = mock_api_instance
    api._fetch_search_queue = AsyncMock(
        return_value={
            "results": [
                {
                    "key": {"href": "https://dummyurl.com/"},
                }
            ]
        }
    )
    try:
        await api.search_enqueue_all("mock_url")
    except KeyError:  # skips checking for last id
        pass
    actual_element = api.queue.get_nowait()
    expected_queue_element = "https://dummyurl.com/"
    assert expected_queue_element == actual_element


async def test_search_worker(mock_api_instance):
    api = mock_api_instance
    api._get_item_queue = AsyncMock(return_value={"id": 3, "name": "test item"})
    api.queue.put_nowait("https://dummyurl.com/")
    actual_result = await api.search_worker("search_item")
    expected_result = {"items": [{"id": 3, "name": "test item"}]}
    await api.close()
    assert expected_result == actual_result


# TODO blocks and never finishes
"""
async def test_get_all_profession_data(mock_api_instance, mock_aioresponses):
    api = mock_api_instance
    api.get_profession_index = AsyncMock(return_value=
        {
        "_links": {
            "self": {
            "href": "https://us.api.blizzard.com/data/wow/profession/?namespace=static-9.2.7_44981-us"
            }
        },
        "professions": [
            {
            "key": {
                "href": "https://us.api.blizzard.com/data/wow/profession/202?namespace=static-9.2.7_44981-us"
            },
            "name": "Engineering",
            "id": 202
            }
        ]
    }
    )
    skill_tier_pattern = re.compile(
        "https://us.api.blizzard.com/data/wow/profession/202?namespace=static-9.2.7_44981-us"
    )
    category_pattern = re.compile(
       'https://us.api.blizzard.com/data/wow/profession/202/skill-tier/2499?namespace=static-9.2.7_44981-us' 
    )
    item_pattern = re.compile(
        "https://us.api.blizzard.com/data/wow/recipe/38895?namespace=static-9.2.7_44981-us"
    )
    skill_tier_data = {
  "_links": {
    "self": {
      "href": "https://us.api.blizzard.com/data/wow/profession/202?namespace=static-9.2.7_44981-us"
    }
  },
  "id": 202,
  "name": "Engineering",
  "description": "Higher engineering skill allows you to learn higher level engineering schematics.  Schematics can be found on trainers around the world as well as from quests and monsters.",
  "type": {
    "type": "PRIMARY",
    "name": "Primary"
  },
  "media": {
    "key": {
      "href": "https://us.api.blizzard.com/data/wow/media/profession/202?namespace=static-9.2.7_44981-us"
    },
    "id": 202
  },
  "skill_tiers": [
    {
      "key": {
        "href": "https://us.api.blizzard.com/data/wow/profession/202/skill-tier/2499?namespace=static-9.2.7_44981-us"
      },
      "name": "Kul Tiran Engineering / Zandalari Engineering",
      "id": 2499
    }]}
    categories_data = {
        "_links": {
            "self": {
            "href": "https://us.api.blizzard.com/data/wow/profession/202/skill-tier/2499?namespace=static-9.2.7_44981-us"
            }
        },
        "id": 2499,
        "name": "Kul Tiran Engineering / Zandalari Engineering",
        "minimum_skill_level": 1,
        "maximum_skill_level": 175,
        "categories": [
            {
            "name": "Bombs",
            "recipes": [
                {
                "key": {
                    "href": "https://us.api.blizzard.com/data/wow/recipe/38895?namespace=static-9.2.7_44981-us"
                },
                "name": "F.R.I.E.D.",
                "id": 38895
                }]}]}
    item_data = {
  "_links": {
    "self": {
      "href": "https://us.api.blizzard.com/data/wow/recipe/38895?namespace=static-9.2.7_44981-us"
    }
  },
  "id": 38895,
  "name": "F.R.I.E.D.",
  "description": "Craft a F.R.I.E.D.",
  "media": {
    "key": {
      "href": "https://us.api.blizzard.com/data/wow/media/recipe/38895?namespace=static-9.2.7_44981-us"
    },
    "id": 38895
  },
  "crafted_item": {
    "key": {
      "href": "https://us.api.blizzard.com/data/wow/item/153490?namespace=static-9.2.7_44981-us"
    },
    "name": "F.R.I.E.D.",
    "id": 153490
  },
  "reagents": [
    {
      "reagent": {
        "key": {
          "href": "https://us.api.blizzard.com/data/wow/item/152512?namespace=static-9.2.7_44981-us"
        },
        "name": "Monelite Ore",
        "id": 152512
      },
      "quantity": 6
    },
    {
      "reagent": {
        "key": {
          "href": "https://us.api.blizzard.com/data/wow/item/160502?namespace=static-9.2.7_44981-us"
        },
        "name": "Chemical Blasting Cap",
        "id": 160502
      },
      "quantity": 5
    },
    {
      "reagent": {
        "key": {
          "href": "https://us.api.blizzard.com/data/wow/item/163569?namespace=static-9.2.7_44981-us"
        },
        "name": "Insulated Wiring",
        "id": 163569
      },
      "quantity": 8
    }
  ],
  "rank": 1,
  "crafted_quantity": {
    "value": 1
  }
}
    
    mock_aioresponses.get(
        skill_tier_pattern,
        status=200,
        payload=skill_tier_data,
    )
    mock_aioresponses.get(
        category_pattern,
        status=200,
        payload=categories_data,
    )
    mock_aioresponses.get(
        item_pattern,
        status=200,
        payload=item_data,
    )

    actual_result = await api.get_all_profession_data()
    expected_result = [
        {
            'name': 'Engineering',
            'id': 202,
            'skill_tiers': [
                {
                    'name': 'Kul Tiran Engineering / Zandalari Engineering',
                    'id': 2499,
                    'categories' : [
                        {
                            'name': 'Bombs',
                            'recipes': [
                                    item_data
                            ]
                        }
                    ]
                }
            ]
        }
    ]
    assert expected_result == actual_result
"""


async def test_connected_realm_search_real(real_api_instance):
    api = real_api_instance
    json = await api.connected_realm_search(**{"_pageSize": 1})
    assert json["results"][0]["data"]["realms"]
    await api.close()


async def test_item_search_real(real_api_instance):
    api = real_api_instance
    json = await api.item_search(**{"_pageSize": 1})
    assert json["results"]
    await api.close()


async def test_get_connected_realms_by_id_real(real_api_instance):
    api = real_api_instance
    json = await api.get_connected_realms_by_id(4)
    assert (
        json["has_queue"] == False or json["has_queue"] == True
    )  # checking if some random parameter is actually returned
    await api.close()


async def test_get_auctions_real(real_api_instance):
    api = real_api_instance
    json = await api.get_auctions(4)
    assert json["auctions"]
    await api.close()


async def test_get_profession_index_real(real_api_instance):
    api = real_api_instance
    json = await api.get_profession_index()
    assert json["professions"]
    await api.close()


async def test_get_profession_tiers_real(real_api_instance):
    api = real_api_instance
    json = await api.get_profession_tiers(164)
    assert json["description"]
    await api.close()


async def test_get_profession_icon_real(real_api_instance):
    api = real_api_instance
    json = await api.get_profession_icon(164)
    assert json["assets"]
    await api.close()


async def test_get_profession_tier_categories_real(real_api_instance):
    api = real_api_instance
    json = await api.get_profession_tier_categories(164, 2437)
    assert json["categories"]
    await api.close()


async def test_get_recipe_real(real_api_instance):
    api = real_api_instance
    json = await api.get_recipe(1631)
    assert json["crafted_item"]
    await api.close()


async def test_get_recipe_icon_real(real_api_instance):
    api = real_api_instance
    json = await api.get_recipe_icon(1631)
    assert json["assets"]
    await api.close()


async def test_get_item_classes_real(real_api_instance):
    api = real_api_instance
    json = await api.get_item_classes()
    assert json["item_classes"]
    await api.close()


async def test_get_item_subclasses_real(real_api_instance):
    api = real_api_instance
    json = await api.get_item_subclasses(17)
    assert json["item_subclasses"]
    await api.close()


async def test_get_item_set_index_real(real_api_instance):
    api = real_api_instance
    json = await api.get_item_set_index()
    assert json["item_sets"]
    await api.close()


async def test_get_item_icon_real(real_api_instance):
    api = real_api_instance
    json = await api.get_item_icon(44151)
    assert json["assets"]
    await api.close()


async def test_get_wow_token_real(real_api_instance):
    api = real_api_instance
    json = await api.get_wow_token()
    assert json["price"]
    await api.close()


async def test_get_connected_realm_index(real_api_instance):
    api = real_api_instance
    json = await api.get_connected_realm_index()
    assert json["connected_realms"]
    await api.close()


# TODO test get all recipe data
