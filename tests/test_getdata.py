import os
import re

import pytest
from aioresponses import aioresponses
import getwowdataasync
from getwowdataasync.getdata import WowApi
from dotenv import load_dotenv


@pytest.fixture
def mock_aioresponses():
    with aioresponses() as mocked:
        yield mocked


@pytest.fixture
async def mock_api_instance(mock_aioresponses):
    data = {"access_token": "dummytoken"}
    #os.environ["wow_api_id"] = "dummyid"
    #os.environ["wow_api_secret"] = "dummysecret"
    mock_aioresponses.post(
        getwowdataasync.urls["access_token"].format(region="us"), status=200, payload=data
    )
    return await getwowdataasync.WowApi.create("us")

@pytest.fixture
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
        headers={"Date": "Tue, 02 Aug 2022 04:05:31 GMT"},
    )
    resp = await api._fetch_get("connected_realm_index")
    await api.close()
    assert resp["key"] == data["key"]


async def test_fetch_search_realms(mock_aioresponses, mock_api_instance):
    api = mock_api_instance
    pattern = re.compile(getwowdataasync.urls["search_realm"].format(region=api.region))
    data = {"key": 1}
    mock_aioresponses.get(
        pattern,
        status=200,
        payload=data,
        headers={"Date": "Tue, 02 Aug 2022 04:05:31 GMT"},
    )
    resp = await api._fetch_get("search_realm")
    await api.close()
    assert resp["key"] == data["key"]


async def test_fetch_search_items(mock_aioresponses, mock_api_instance):
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
        headers={"Date": "Tue, 02 Aug 2022 04:05:31 GMT"},
    )
    mock_aioresponses.get(
        pattern_dummyurl,
        status=200,
        payload=item_data,
        headers={"Date": "Tue, 02 Aug 2022 04:05:31 GMT"},
    )

    resp = await api._fetch_search("search_item", {"id": "1"})
    await api.close()
    expected_resp = {
        "items": [{"item": 1, "dummyvalue": 2}],
        "Date": "Tue, 02 Aug 2022 04:05:31 GMT",
    }
    assert resp == expected_resp

async def test_connected_realm_search_real(real_api_instance):
    api = real_api_instance
    json = await api.connected_realm_search()
    assert json['results']
    await api.close()

    
async def test_item_search_real(real_api_instance):
    api = real_api_instance
    json = await api.item_search()
    assert json['items']
    await api.close()


async def test_get_connected_realms_by_id_real(real_api_instance):
    api = real_api_instance
    json = await api.get_connected_realms_by_id(4)
    assert json['has_queue'] == False or json['has_queue'] == True #checking if some random parameter is actually returned
    await api.close()


async def test_get_auctions_real(real_api_instance):
    api = real_api_instance
    json = await api.get_auctions(4)
    assert json['auctions']
    await api.close()


async def test_get_profession_index_real(real_api_instance):
    api = real_api_instance
    json = await api.get_profession_index()
    assert json['professions']
    await api.close()


async def test_get_profession_tiers_real(real_api_instance):
    api = real_api_instance
    json = await api.get_profession_tiers(164)
    assert json['description']
    await api.close()


async def test_get_profession_icon_real(real_api_instance):
    api = real_api_instance
    json = await api.get_profession_icon(164)
    assert json['assets']
    await api.close()


async def test_get_profession_tier_categories_real(real_api_instance):
    api = real_api_instance
    json = await api.get_profession_tier_categories(164, 2437)
    assert json['categories']
    await api.close()


async def test_get_recipe_real(real_api_instance):
    api = real_api_instance
    json = await api.get_recipe(1631)
    assert json['crafted_item']
    await api.close()


async def test_get_recipe_icon_real(real_api_instance):
    api = real_api_instance
    json = await api.get_recipe_icon(1631)
    assert json['assets']
    await api.close()


async def test_get_item_classes_real(real_api_instance):
    api = real_api_instance
    json = await api.get_item_classes()
    assert json['item_classes']
    await api.close()


async def test_get_item_subclasses_real(real_api_instance):
    api = real_api_instance
    json = await api.get_item_subclasses(17)
    assert json['item_subclasses']
    await api.close()


async def test_get_item_set_index_real(real_api_instance):
    api = real_api_instance
    json = await api.get_item_set_index()
    assert json['item_sets']
    await api.close()


async def test_get_item_icon_real(real_api_instance):
    api = real_api_instance
    json = await api.get_item_icon(44151)
    assert json['assets']
    await api.close()


async def test_get_wow_token_real(real_api_instance):
    api = real_api_instance
    json = await api.get_wow_token()
    assert json['price']
    await api.close()

async def test_get_connected_realm_index(real_api_instance):
    api = real_api_instance
    json = await api.get_connected_realm_index()
    assert json['connected_realms']
    await api.close()
