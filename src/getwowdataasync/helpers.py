"""This module contains functions that preform common tasks."""
import re
import datetime
import functools
import asyncio

import aiohttp
# Importing WowApi into this file caueses a circulat import error when running tests


def as_gold(amount: int) -> str:
    """Formats a integer as n*g nns nnc where n is some number, g = gold, s = silver, and c = copper.

    Args:
        amount (int): The value of something in WoW's currency.

    Returns:
        A string formatted to WoW's gold, silver, copper currency.
    """
    if amount >= 0:
        return f"{int(str(amount)[:-4]):,}g {str(amount)[-4:-2]}s {str(amount)[-2:]}c"
    else:
        return f"{int(str(amount)[:-4]):,}g {str(amount)[-4:-2]}s {str(amount)[-2:]}c"


def get_id_from_url(url: str) -> int:
    """Returns the id from a url.

        This matches to the first number in a string. As of writing the only number
        in blizzard's urls is an id.

    Args:
        url (str): The url that contains a single number id.

    Returns:
        The number found in the url.
    """
    pattern = re.compile(r"[\d]+")
    return pattern.search(url).group()


def convert_to_datetime(Date: str):
    """Takes last-modified header and converts it to a datetime object."""
    # last-modified: Mon, 27 Jun 2022 18:28:56 GMT
    months = {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12,
    }
    months_pattern = re.compile(r"Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec")
    nums = re.findall(r"\d+", Date)
    month_str = re.search(months_pattern, Date).group()
    month = months[month_str]
    day = int(nums[0])
    year = int(nums[1])
    hour = int(nums[2])
    min = int(nums[3])
    sec = int(nums[4])

    return datetime.datetime(year, month, day, hour=hour, minute=min, second=sec)

def retry(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        retries = 0
        while retries < 10:
            try:
                json = await func(*args, **kwargs)
                await asyncio.sleep(1)
                return json
            except aiohttp.ClientConnectionError as e:
                print(f"{func.__name__} {e}")
                retries += 1
            except aiohttp.ClientResponseError as e:
                print(f"{func.__name__} {e}")
                retries += 1
            except aiohttp.ClientPayloadError as e:
                print(f"{func.__name__} {e}")
                retries += 1

    return wrapper

# This is probally useless but i don't want to delete it completely
# def retry_queue(func):
#     @functools.wraps(func)
#     async def wrapper(WowApi: WowApi ,*args, **kwargs):
#         try:
#             self = args[0]
#             json = await func(*args, **kwargs)
#             return json
#         except aiohttp.ClientConnectionError as e:
#             print(f"{func.__name__} {e}")
#             self = args[0] # This is needed since the args are passed at runtime
#             self.queue.put_nowait(args[1]) # args[1] is the function being decorated
#         except aiohttp.ClientResponseError as e:
#             print(f"{func.__name__} {e}")
#             args[0].queue.put_nowait(args[1])
#         except aiohttp.ClientPayloadError as e:
#             print(f"{func.__name__} {e}")
#             args[0].queue.put_nowait(args[1])

#     return wrapper
