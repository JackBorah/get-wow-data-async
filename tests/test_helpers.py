import unittest
from unittest.mock import AsyncMock

from getwowdataasync.helpers import *

class TestHelpers(unittest.IsolatedAsyncioTestCase):
    async def test_retry_retries_10_times_on_ClientConnectionError(self):
        test_func = AsyncMock(side_effect=aiohttp.ClientConnectionError)
        test_func.__name__ = ''

        decorated_test_func = retry(test_func)
        await decorated_test_func()

        actual_retry_count = test_func.await_count
        expected_retry_count = 10

        self.assertEqual(expected_retry_count, actual_retry_count)

    # TODO
    # Unsure how to do this since the ResponseError requires
    # arguments of a specific type that i don't know how to mock
    # I also don't know if I can mock the exception so it doesn't
    # need those variables
    # @patch('aiohttp.ClientResponseError')
    # async def test_retry_retries_10_times_on_ClientResponseError(self, mock_ClientResponseError):
    #     mock_ClientResponseError = AsyncMock(autospec=ClientResponseError)
    #     test_func = AsyncMock(side_effect=mock_ClientResponseError)
    #     test_func.__name__ = 'test_func'

    #     decorator = retry()
    #     decorated_func = decorator(test_func)
    #     await decorated_func()

    #     actual_retry_count = test_func.await_count
    #     expected_retry_count = 10

    #     self.assertEqual(expected_retry_count, actual_retry_count)

    async def test_retry_retries_10_times_on_ClientPayloadError(self):
        test_func = AsyncMock(side_effect=aiohttp.ClientPayloadError)
        test_func.__name__ = ''

        decorated_func = retry(test_func)
        await decorated_func()

        actual_retry_count = test_func.await_count
        expected_retry_count = 10

        self.assertEqual(expected_retry_count, actual_retry_count)

    async def test_retry_correctly_executes_decorated_function(self):
        test_func = AsyncMock()
        test_func.__name__ = ''

        decorated_func = retry(test_func)
        await decorated_func()

        actual_retry_count = test_func.await_count
        expected_retry_count = 1

        self.assertEqual(expected_retry_count, actual_retry_count)

if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    unittest.main()