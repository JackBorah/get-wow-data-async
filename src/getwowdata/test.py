import asyncio
import os
import re

import aiohttp
import pytest
import pytest_asyncio
from aioresponses import aioresponses
import getwowdata
from getwowdata.getdata import WowApi

@pytest.fixture
def mock_aioresponses():
    with aioresponses() as mocked:
        yield mocked

@pytest.fixture
@pytest.mark.asyncio
async def api_instance(mock_aioresponses):
    data = {'access_token':'dummytoken'}
    os.environ['wow_api_id'] = 'dummyid'
    os.environ['wow_api_secret'] = 'dummysecret'
    mock_aioresponses.post(getwowdata.urls['access_token'].format(region='us'), status=200, payload=data)
    return await getwowdata.WowApi.create('us')


@pytest.mark.asyncio
async def test_get_access_token(api_instance):
    api = await api_instance
    await api.close()
    assert api.access_token == 'dummytoken'


@pytest.mark.asyncio
async def test_fetch_get(mock_aioresponses, api_instance):
    api = await api_instance
    pattern = re.compile(getwowdata.urls['connected_realm_index'].format(region=api.region))
    data = {'key':1}
    mock_aioresponses.get(pattern, status=200, payload=data, headers={'Date':'Tue, 02 Aug 2022 04:05:31 GMT'})
    resp = await api._fetch_get('connected_realm_index')
    assert resp['key'] == data['key']

