import os
import re

import pytest
from aioresponses import aioresponses
import getwowdata
from getwowdata.getdata import WowApi


@pytest.fixture
def mock_aioresponses():
    with aioresponses() as mocked:
        yield mocked


@pytest.fixture
async def api_instance(mock_aioresponses):
    data = {"access_token": "dummytoken"}
    os.environ["wow_api_id"] = "dummyid"
    os.environ["wow_api_secret"] = "dummysecret"
    mock_aioresponses.post(
        getwowdata.urls["access_token"].format(region="us"), status=200, payload=data
    )
    return await getwowdata.WowApi.create("us")


async def test_get_access_token(api_instance):
    api = api_instance
    await api.close()
    assert api.access_token == "dummytoken"


async def test_fetch_get_returns_json(mock_aioresponses, api_instance):
    api = api_instance
    pattern = re.compile(
        getwowdata.urls["connected_realm_index"].format(region=api.region)
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


async def test_fetch_get_returns_binary(mock_aioresponses, api_instance):
    api = api_instance
    pattern = re.compile(
        getwowdata.urls["item_icon"].format(region=api.region, item_id=1)
    )
    data = {"key": 1}
    mock_aioresponses.get(
        pattern,
        status=200,
        payload=data,
        headers={"Date": "Tue, 02 Aug 2022 04:05:31 GMT"},
    )
    resp = await api._fetch_get("item_icon", ids={"item_id": 1})
    await api.close()
    assert type(resp) == type(b"")


async def test_fetch_search_realms(mock_aioresponses, api_instance):
    api = api_instance
    pattern = re.compile(getwowdata.urls["search_realm"].format(region=api.region))
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


async def test_fetch_search_items(mock_aioresponses, api_instance):
    api = api_instance
    search_pattern = re.compile(
        getwowdata.urls["search_item"].format(region=api.region)
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
