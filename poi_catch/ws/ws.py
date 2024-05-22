import json
import time
import aiohttp

import hashlib
from urllib.parse import quote


def sess_tx() -> aiohttp.ClientSession:
    return aiohttp.ClientSession("https://apis.map.qq.com", headers={
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0"
    })


def parse_params_tx(uri: str, params: dict, SK: str) -> str:
    params_str = '&'.join(
        [f"{key}={value}" for key, value in sorted(params.items())])
    uri = f"{uri}?{params_str}"
    sig = hashlib.md5((uri+SK).encode()).hexdigest()
    uri = f"{uri}&sig={sig}"
    return uri


async def poi_search_tx(sess: aiohttp.ClientSession, key: str, SK: str, keyword: str, city: str, pn: int = 1) -> dict:
    place_search_uri = "/ws/place/v1/search"
    params = {
        "key": key,
        "keyword": keyword,
        "boundary": f"region({city},0)",
        "page_size": 10,
        "page_index": pn,
    }
    place_search_uri = parse_params_tx(place_search_uri, params, SK)
    async with sess.get(place_search_uri) as resp:
        return await resp.json()


def sess_360() -> aiohttp.ClientSession:
    return aiohttp.ClientSession("https://restapi.map.360.cn", headers={
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0"
    })


async def poi_search_360(sess: aiohttp.ClientSession, keyword: str, city: str, pn: int = 1) -> dict:
    params = {
        "keyword": keyword,
        "cityname": city,
        "d": "pc",
        "brand_cpc": "on",
        "batch": pn,
        "number": 10,
        "qii": "true",
        "scheme": "https",
        "regionType": "rectangle",
        "sid": 1000,
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
        "browser_size": "1232,1059",
        "screen_size": "2560,1440",
        "screen_pixel_ratio": 1,
        "_": time.time_ns()//10**6
    }
    uri = "/newapi"
    # uri = "/app/pit"
    params_str = '&'.join(
        [f"{key}={value}" for key, value in sorted(params.items())])
    uri = f"{uri}?{params_str}"
    async with sess.get(uri) as resp:
        if resp.status == 200:
            return await resp.json()
        return {}


def sess_baidu() -> aiohttp.ClientSession:
    return aiohttp.ClientSession("https://map.baidu.com", headers={
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0"
    })


async def poi_search_baidu(sess: aiohttp.ClientSession, keyword: str, city: str, pn: int = 1) -> dict:
    resp = await sess.get(f"/?qt=cur&wd={city}")
    data = json.loads(await resp.read())
    if "content" not in data:
        return {}
    cid = data["content"]["area"]
    resp = await sess.get(f"/?qt=spot&c={cid}&wd={keyword}&pn={pn}")
    return json.loads(await resp.read())
